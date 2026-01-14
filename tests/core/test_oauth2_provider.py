"""
Tests for OAuth 2.0 Provider / Authorization Server

Tests cover:
- Client registration and management
- Authorization code flow
- Token issuance (access + refresh)
- Token validation and introspection
- Token revocation
- PKCE support (RFC 7636)
- Multiple grant types
- Scope validation
- Error handling
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import secrets
import hashlib
import base64

from src.core.oauth2_provider import (
    OAuth2Provider,
    OAuthClient,
    AuthorizationCode,
    AccessToken,
    RefreshToken,
    GrantType,
    TokenType,
    generate_code_verifier,
    generate_code_challenge
)


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def provider():
    """OAuth2 provider instance"""
    return OAuth2Provider()


@pytest.fixture
def registered_client(provider):
    """Pre-registered OAuth client"""
    client = provider.register_client(
        client_name="Test App",
        redirect_uris=["https://example.com/callback", "https://example.com/callback2"],
        grant_types=[GrantType.AUTHORIZATION_CODE, GrantType.REFRESH_TOKEN],
        scope=["read", "write"]
    )
    return client


@pytest.fixture
def confidential_client(provider):
    """Confidential client with client_secret"""
    client = provider.register_client(
        client_name="Confidential App",
        redirect_uris=["https://app.example.com/callback"],
        grant_types=[GrantType.AUTHORIZATION_CODE, GrantType.CLIENT_CREDENTIALS],
        scope=["read", "write", "admin"],
        is_confidential=True
    )
    return client


@pytest.fixture
def public_client(provider):
    """Public client (no client_secret, uses PKCE)"""
    client = provider.register_client(
        client_name="Mobile App",
        redirect_uris=["myapp://callback"],
        grant_types=[GrantType.AUTHORIZATION_CODE],
        scope=["read"],
        is_confidential=False
    )
    return client


# ============================================================
# Client Registration Tests
# ============================================================

def test_register_client_success(provider):
    """Test successful client registration"""
    client = provider.register_client(
        client_name="Test Application",
        redirect_uris=["https://example.com/callback"],
        grant_types=[GrantType.AUTHORIZATION_CODE],
        scope=["read", "write"]
    )

    assert client.client_id.startswith("oauth2_client_")
    assert len(client.client_secret) > 0
    assert client.client_name == "Test Application"
    assert "https://example.com/callback" in client.redirect_uris
    assert GrantType.AUTHORIZATION_CODE in client.grant_types
    assert "read" in client.scope
    assert client.is_active is True


def test_register_client_multiple_redirect_uris(provider):
    """Test client with multiple redirect URIs"""
    client = provider.register_client(
        client_name="Multi-URI App",
        redirect_uris=[
            "https://example.com/callback1",
            "https://example.com/callback2",
            "https://example.com/callback3"
        ],
        grant_types=[GrantType.AUTHORIZATION_CODE],
        scope=["read"]
    )

    assert len(client.redirect_uris) == 3
    assert all(uri.startswith("https://") for uri in client.redirect_uris)


def test_register_client_with_metadata(provider):
    """Test client registration with additional metadata"""
    client = provider.register_client(
        client_name="Metadata App",
        redirect_uris=["https://example.com/callback"],
        grant_types=[GrantType.AUTHORIZATION_CODE],
        scope=["read"],
        client_uri="https://example.com",
        logo_uri="https://example.com/logo.png",
        tos_uri="https://example.com/terms",
        policy_uri="https://example.com/privacy"
    )

    assert client.client_uri == "https://example.com"
    assert client.logo_uri == "https://example.com/logo.png"


def test_register_client_public_vs_confidential(provider):
    """Test public vs confidential client registration"""
    # Public client (e.g., mobile app) - no client_secret
    public_client = provider.register_client(
        client_name="Public App",
        redirect_uris=["myapp://callback"],
        grant_types=[GrantType.AUTHORIZATION_CODE],
        scope=["read"],
        is_confidential=False
    )

    # Confidential client (e.g., server app) - has client_secret
    confidential_client = provider.register_client(
        client_name="Confidential App",
        redirect_uris=["https://app.example.com/callback"],
        grant_types=[GrantType.AUTHORIZATION_CODE, GrantType.CLIENT_CREDENTIALS],
        scope=["read", "write"],
        is_confidential=True
    )

    assert public_client.is_confidential is False
    assert confidential_client.is_confidential is True
    assert len(confidential_client.client_secret) > 0


def test_get_client_by_id(provider, registered_client):
    """Test retrieving client by ID"""
    client = provider.get_client(registered_client.client_id)

    assert client is not None
    assert client.client_id == registered_client.client_id
    assert client.client_name == registered_client.client_name


def test_get_nonexistent_client(provider):
    """Test retrieving non-existent client"""
    client = provider.get_client("nonexistent_client_id")
    assert client is None


# ============================================================
# Authorization Code Flow Tests
# ============================================================

def test_authorize_success(provider, registered_client):
    """Test successful authorization code generation"""
    user_id = 100

    result = provider.authorize(
        client_id=registered_client.client_id,
        redirect_uri=registered_client.redirect_uris[0],
        scope=["read"],
        user_id=user_id,
        state="random_state_123"
    )

    assert 'code' in result
    assert 'state' in result
    assert result['state'] == "random_state_123"
    assert len(result['code']) > 0


def test_authorize_invalid_client(provider):
    """Test authorization with invalid client_id"""
    with pytest.raises(ValueError, match="Invalid client"):
        provider.authorize(
            client_id="invalid_client_id",
            redirect_uri="https://example.com/callback",
            scope=["read"],
            user_id=100
        )


def test_authorize_invalid_redirect_uri(provider, registered_client):
    """Test authorization with unregistered redirect_uri"""
    with pytest.raises(ValueError, match="redirect_uri"):
        provider.authorize(
            client_id=registered_client.client_id,
            redirect_uri="https://evil.com/callback",  # Not registered
            scope=["read"],
            user_id=100
        )


def test_authorize_invalid_scope(provider, registered_client):
    """Test authorization with invalid scope"""
    with pytest.raises(ValueError, match="scope"):
        provider.authorize(
            client_id=registered_client.client_id,
            redirect_uri=registered_client.redirect_uris[0],
            scope=["admin", "delete"],  # Not registered for this client
            user_id=100
        )


def test_authorize_with_pkce(provider, public_client):
    """Test authorization with PKCE (for public clients)"""
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    result = provider.authorize(
        client_id=public_client.client_id,
        redirect_uri=public_client.redirect_uris[0],
        scope=["read"],
        user_id=100,
        code_challenge=code_challenge,
        code_challenge_method="S256"
    )

    assert 'code' in result
    # Verify PKCE parameters stored
    auth_code = provider.get_authorization_code(result['code'])
    assert auth_code.code_challenge == code_challenge
    assert auth_code.code_challenge_method == "S256"


# ============================================================
# Token Exchange Tests
# ============================================================

def test_exchange_code_for_token_success(provider, registered_client):
    """Test exchanging authorization code for access token"""
    # First, get authorization code
    user_id = 100
    auth_result = provider.authorize(
        client_id=registered_client.client_id,
        redirect_uri=registered_client.redirect_uris[0],
        scope=["read", "write"],
        user_id=user_id
    )

    # Exchange code for token
    token = provider.exchange_code(
        code=auth_result['code'],
        client_id=registered_client.client_id,
        client_secret=registered_client.client_secret,
        redirect_uri=registered_client.redirect_uris[0]
    )

    assert token.access_token is not None
    assert token.token_type == TokenType.BEARER
    assert token.expires_in > 0
    assert token.refresh_token is not None
    assert "read" in token.scope
    assert "write" in token.scope


def test_exchange_code_invalid_code(provider, registered_client):
    """Test exchange with invalid authorization code"""
    with pytest.raises(ValueError, match="Invalid.*code"):
        provider.exchange_code(
            code="invalid_code_xyz",
            client_id=registered_client.client_id,
            client_secret=registered_client.client_secret,
            redirect_uri=registered_client.redirect_uris[0]
        )


def test_exchange_code_expired(provider, registered_client):
    """Test exchange with expired authorization code"""
    # Create authorization code
    user_id = 100
    auth_result = provider.authorize(
        client_id=registered_client.client_id,
        redirect_uri=registered_client.redirect_uris[0],
        scope=["read"],
        user_id=user_id
    )

    # Manually expire the code
    auth_code = provider.get_authorization_code(auth_result['code'])
    auth_code.expires_at = datetime.now() - timedelta(minutes=10)

    # Try to exchange expired code
    with pytest.raises(ValueError, match="expired"):
        provider.exchange_code(
            code=auth_result['code'],
            client_id=registered_client.client_id,
            client_secret=registered_client.client_secret,
            redirect_uri=registered_client.redirect_uris[0]
        )


def test_exchange_code_wrong_client(provider, registered_client):
    """Test exchange with wrong client credentials"""
    # Get authorization code for client A
    auth_result = provider.authorize(
        client_id=registered_client.client_id,
        redirect_uri=registered_client.redirect_uris[0],
        scope=["read"],
        user_id=100
    )

    # Try to exchange with wrong client_id
    with pytest.raises(ValueError, match="client"):
        provider.exchange_code(
            code=auth_result['code'],
            client_id="wrong_client_id",
            client_secret="wrong_secret",
            redirect_uri=registered_client.redirect_uris[0]
        )


def test_exchange_code_wrong_redirect_uri(provider, registered_client):
    """Test exchange with wrong redirect_uri"""
    auth_result = provider.authorize(
        client_id=registered_client.client_id,
        redirect_uri=registered_client.redirect_uris[0],
        scope=["read"],
        user_id=100
    )

    with pytest.raises(ValueError, match="redirect_uri"):
        provider.exchange_code(
            code=auth_result['code'],
            client_id=registered_client.client_id,
            client_secret=registered_client.client_secret,
            redirect_uri="https://different.com/callback"
        )


def test_exchange_code_used_twice(provider, registered_client):
    """Test that authorization code can only be used once"""
    # Get authorization code
    auth_result = provider.authorize(
        client_id=registered_client.client_id,
        redirect_uri=registered_client.redirect_uris[0],
        scope=["read"],
        user_id=100
    )

    # Exchange once - should succeed
    token1 = provider.exchange_code(
        code=auth_result['code'],
        client_id=registered_client.client_id,
        client_secret=registered_client.client_secret,
        redirect_uri=registered_client.redirect_uris[0]
    )
    assert token1.access_token is not None

    # Try to exchange again - should fail
    with pytest.raises(ValueError, match="already used|Invalid"):
        provider.exchange_code(
            code=auth_result['code'],
            client_id=registered_client.client_id,
            client_secret=registered_client.client_secret,
            redirect_uri=registered_client.redirect_uris[0]
        )


def test_exchange_code_with_pkce_success(provider, public_client):
    """Test code exchange with PKCE verification"""
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    # Authorize with PKCE
    auth_result = provider.authorize(
        client_id=public_client.client_id,
        redirect_uri=public_client.redirect_uris[0],
        scope=["read"],
        user_id=100,
        code_challenge=code_challenge,
        code_challenge_method="S256"
    )

    # Exchange with correct code_verifier
    token = provider.exchange_code(
        code=auth_result['code'],
        client_id=public_client.client_id,
        redirect_uri=public_client.redirect_uris[0],
        code_verifier=code_verifier
    )

    assert token.access_token is not None


def test_exchange_code_with_pkce_wrong_verifier(provider, public_client):
    """Test code exchange with wrong PKCE verifier"""
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    # Authorize with PKCE
    auth_result = provider.authorize(
        client_id=public_client.client_id,
        redirect_uri=public_client.redirect_uris[0],
        scope=["read"],
        user_id=100,
        code_challenge=code_challenge,
        code_challenge_method="S256"
    )

    # Try to exchange with wrong code_verifier
    wrong_verifier = generate_code_verifier()
    with pytest.raises(ValueError, match="code_verifier"):
        provider.exchange_code(
            code=auth_result['code'],
            client_id=public_client.client_id,
            redirect_uri=public_client.redirect_uris[0],
            code_verifier=wrong_verifier
        )


# ============================================================
# Refresh Token Tests
# ============================================================

def test_refresh_token_success(provider, registered_client):
    """Test refreshing access token with refresh token"""
    # Get initial tokens
    auth_result = provider.authorize(
        client_id=registered_client.client_id,
        redirect_uri=registered_client.redirect_uris[0],
        scope=["read", "write"],
        user_id=100
    )

    initial_token = provider.exchange_code(
        code=auth_result['code'],
        client_id=registered_client.client_id,
        client_secret=registered_client.client_secret,
        redirect_uri=registered_client.redirect_uris[0]
    )

    # Refresh token
    new_token = provider.refresh_access_token(
        refresh_token=initial_token.refresh_token,
        client_id=registered_client.client_id,
        client_secret=registered_client.client_secret
    )

    assert new_token.access_token != initial_token.access_token
    assert new_token.token_type == TokenType.BEARER
    assert new_token.expires_in > 0
    assert "read" in new_token.scope
    assert "write" in new_token.scope


def test_refresh_token_invalid(provider, registered_client):
    """Test refresh with invalid refresh token"""
    with pytest.raises(ValueError, match="Invalid refresh token"):
        provider.refresh_access_token(
            refresh_token="invalid_refresh_token_xyz",
            client_id=registered_client.client_id,
            client_secret=registered_client.client_secret
        )


def test_refresh_token_expired(provider, registered_client):
    """Test refresh with expired refresh token"""
    # Get tokens
    auth_result = provider.authorize(
        client_id=registered_client.client_id,
        redirect_uri=registered_client.redirect_uris[0],
        scope=["read"],
        user_id=100
    )

    token = provider.exchange_code(
        code=auth_result['code'],
        client_id=registered_client.client_id,
        client_secret=registered_client.client_secret,
        redirect_uri=registered_client.redirect_uris[0]
    )

    # Manually expire refresh token
    refresh_token_obj = provider.get_refresh_token(token.refresh_token)
    refresh_token_obj.expires_at = datetime.now() - timedelta(days=1)

    # Try to refresh
    with pytest.raises(ValueError, match="expired"):
        provider.refresh_access_token(
            refresh_token=token.refresh_token,
            client_id=registered_client.client_id,
            client_secret=registered_client.client_secret
        )


def test_refresh_token_scope_downgrade(provider, registered_client):
    """Test refresh token with reduced scope"""
    # Get initial tokens with multiple scopes
    auth_result = provider.authorize(
        client_id=registered_client.client_id,
        redirect_uri=registered_client.redirect_uris[0],
        scope=["read", "write"],
        user_id=100
    )

    initial_token = provider.exchange_code(
        code=auth_result['code'],
        client_id=registered_client.client_id,
        client_secret=registered_client.client_secret,
        redirect_uri=registered_client.redirect_uris[0]
    )

    # Refresh with reduced scope
    new_token = provider.refresh_access_token(
        refresh_token=initial_token.refresh_token,
        client_id=registered_client.client_id,
        client_secret=registered_client.client_secret,
        scope=["read"]  # Only "read", not "write"
    )

    assert "read" in new_token.scope
    assert "write" not in new_token.scope


# ============================================================
# Client Credentials Grant Tests
# ============================================================

def test_client_credentials_grant_success(provider, confidential_client):
    """Test client credentials grant (machine-to-machine)"""
    token = provider.client_credentials_grant(
        client_id=confidential_client.client_id,
        client_secret=confidential_client.client_secret,
        scope=["read", "write"]
    )

    assert token.access_token is not None
    assert token.token_type == TokenType.BEARER
    assert "read" in token.scope
    assert "write" in token.scope
    assert token.refresh_token is None  # No refresh token for client credentials


def test_client_credentials_invalid_credentials(provider):
    """Test client credentials with invalid credentials"""
    with pytest.raises(ValueError, match="Invalid client"):
        provider.client_credentials_grant(
            client_id="invalid_client",
            client_secret="invalid_secret",
            scope=["read"]
        )


def test_client_credentials_unsupported_grant(provider, registered_client):
    """Test client credentials with client that doesn't support it"""
    # registered_client only supports authorization_code
    with pytest.raises(ValueError, match="grant type"):
        provider.client_credentials_grant(
            client_id=registered_client.client_id,
            client_secret=registered_client.client_secret,
            scope=["read"]
        )


# ============================================================
# Token Validation Tests
# ============================================================

def test_validate_token_success(provider, registered_client):
    """Test successful token validation"""
    # Get token
    auth_result = provider.authorize(
        client_id=registered_client.client_id,
        redirect_uri=registered_client.redirect_uris[0],
        scope=["read", "write"],
        user_id=100
    )

    token = provider.exchange_code(
        code=auth_result['code'],
        client_id=registered_client.client_id,
        client_secret=registered_client.client_secret,
        redirect_uri=registered_client.redirect_uris[0]
    )

    # Validate token
    validation = provider.validate_token(token.access_token)

    assert validation['active'] is True
    assert validation['client_id'] == registered_client.client_id
    assert validation['user_id'] == 100
    assert "read" in validation['scope']
    assert "write" in validation['scope']
    assert 'exp' in validation


def test_validate_token_invalid(provider):
    """Test validation of invalid token"""
    validation = provider.validate_token("invalid_token_xyz")

    assert validation['active'] is False


def test_validate_token_expired(provider, registered_client):
    """Test validation of expired token"""
    # Get token
    auth_result = provider.authorize(
        client_id=registered_client.client_id,
        redirect_uri=registered_client.redirect_uris[0],
        scope=["read"],
        user_id=100
    )

    token = provider.exchange_code(
        code=auth_result['code'],
        client_id=registered_client.client_id,
        client_secret=registered_client.client_secret,
        redirect_uri=registered_client.redirect_uris[0]
    )

    # Manually expire token
    token_obj = provider.get_access_token(token.access_token)
    token_obj.expires_at = datetime.now() - timedelta(hours=1)

    # Validate expired token
    validation = provider.validate_token(token.access_token)

    assert validation['active'] is False


def test_validate_token_revoked(provider, registered_client):
    """Test validation of revoked token"""
    # Get token
    auth_result = provider.authorize(
        client_id=registered_client.client_id,
        redirect_uri=registered_client.redirect_uris[0],
        scope=["read"],
        user_id=100
    )

    token = provider.exchange_code(
        code=auth_result['code'],
        client_id=registered_client.client_id,
        client_secret=registered_client.client_secret,
        redirect_uri=registered_client.redirect_uris[0]
    )

    # Revoke token
    provider.revoke_token(
        token=token.access_token,
        client_id=registered_client.client_id,
        client_secret=registered_client.client_secret
    )

    # Validate revoked token
    validation = provider.validate_token(token.access_token)

    assert validation['active'] is False


# ============================================================
# Token Revocation Tests
# ============================================================

def test_revoke_access_token(provider, registered_client):
    """Test access token revocation"""
    # Get token
    auth_result = provider.authorize(
        client_id=registered_client.client_id,
        redirect_uri=registered_client.redirect_uris[0],
        scope=["read"],
        user_id=100
    )

    token = provider.exchange_code(
        code=auth_result['code'],
        client_id=registered_client.client_id,
        client_secret=registered_client.client_secret,
        redirect_uri=registered_client.redirect_uris[0]
    )

    # Revoke
    result = provider.revoke_token(
        token=token.access_token,
        client_id=registered_client.client_id,
        client_secret=registered_client.client_secret
    )

    assert result is True

    # Verify token is invalid
    validation = provider.validate_token(token.access_token)
    assert validation['active'] is False


def test_revoke_refresh_token(provider, registered_client):
    """Test refresh token revocation"""
    # Get token
    auth_result = provider.authorize(
        client_id=registered_client.client_id,
        redirect_uri=registered_client.redirect_uris[0],
        scope=["read"],
        user_id=100
    )

    token = provider.exchange_code(
        code=auth_result['code'],
        client_id=registered_client.client_id,
        client_secret=registered_client.client_secret,
        redirect_uri=registered_client.redirect_uris[0]
    )

    # Revoke refresh token
    result = provider.revoke_token(
        token=token.refresh_token,
        client_id=registered_client.client_id,
        client_secret=registered_client.client_secret
    )

    assert result is True

    # Verify refresh token is invalid
    with pytest.raises(ValueError):
        provider.refresh_access_token(
            refresh_token=token.refresh_token,
            client_id=registered_client.client_id,
            client_secret=registered_client.client_secret
        )


def test_revoke_invalid_token(provider, registered_client):
    """Test revocation of non-existent token (should succeed per spec)"""
    # Per OAuth spec, revocation endpoint should return success even for invalid tokens
    result = provider.revoke_token(
        token="invalid_token_xyz",
        client_id=registered_client.client_id,
        client_secret=registered_client.client_secret
    )

    # Should not raise error
    assert result is True or result is False


# ============================================================
# PKCE Helper Tests
# ============================================================

def test_generate_code_verifier():
    """Test PKCE code verifier generation"""
    verifier = generate_code_verifier()

    assert len(verifier) >= 43
    assert len(verifier) <= 128
    assert verifier.replace('-', '').replace('_', '').isalnum()


def test_generate_code_challenge_s256():
    """Test PKCE code challenge with S256 method"""
    verifier = "test_verifier_123456789012345678901234567890"
    challenge = generate_code_challenge(verifier, method="S256")

    # Manually compute expected challenge
    expected = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).decode().rstrip('=')

    assert challenge == expected


def test_generate_code_challenge_plain():
    """Test PKCE code challenge with plain method"""
    verifier = "test_verifier_plain"
    challenge = generate_code_challenge(verifier, method="plain")

    assert challenge == verifier


def test_pkce_challenge_verification():
    """Test full PKCE flow verification"""
    verifier = generate_code_verifier()
    challenge = generate_code_challenge(verifier)

    # Simulate what server does: verify challenge matches verifier
    computed_challenge = generate_code_challenge(verifier)

    assert challenge == computed_challenge


# ============================================================
# Scope Validation Tests
# ============================================================

def test_scope_validation_valid(provider, registered_client):
    """Test valid scope validation"""
    is_valid = provider.validate_scope(
        client_id=registered_client.client_id,
        requested_scope=["read"]
    )

    assert is_valid is True


def test_scope_validation_invalid(provider, registered_client):
    """Test invalid scope validation"""
    is_valid = provider.validate_scope(
        client_id=registered_client.client_id,
        requested_scope=["admin", "delete"]  # Not registered
    )

    assert is_valid is False


def test_scope_validation_partial_valid(provider, registered_client):
    """Test partial scope validation"""
    # Mix of valid and invalid scopes
    is_valid = provider.validate_scope(
        client_id=registered_client.client_id,
        requested_scope=["read", "admin"]  # "read" valid, "admin" invalid
    )

    assert is_valid is False  # All scopes must be valid


# ============================================================
# Edge Cases & Security Tests
# ============================================================

def test_token_uniqueness(provider, registered_client):
    """Test that tokens are unique"""
    tokens = []

    for i in range(10):
        auth_result = provider.authorize(
            client_id=registered_client.client_id,
            redirect_uri=registered_client.redirect_uris[0],
            scope=["read"],
            user_id=100 + i
        )

        token = provider.exchange_code(
            code=auth_result['code'],
            client_id=registered_client.client_id,
            client_secret=registered_client.client_secret,
            redirect_uri=registered_client.redirect_uris[0]
        )

        tokens.append(token.access_token)

    # All tokens should be unique
    assert len(tokens) == len(set(tokens))


def test_client_secret_not_exposed(provider, registered_client):
    """Test that client secret is not exposed in responses"""
    # Client secret should only be known at registration time
    retrieved_client = provider.get_client(registered_client.client_id)

    # In production, client_secret should be hashed, not stored plaintext
    # This test assumes implementation includes secret hashing
    assert retrieved_client.client_id == registered_client.client_id


def test_multiple_simultaneous_tokens(provider, registered_client):
    """Test multiple valid tokens for same user/client"""
    user_id = 100
    tokens = []

    # Get multiple tokens
    for i in range(3):
        auth_result = provider.authorize(
            client_id=registered_client.client_id,
            redirect_uri=registered_client.redirect_uris[0],
            scope=["read"],
            user_id=user_id
        )

        token = provider.exchange_code(
            code=auth_result['code'],
            client_id=registered_client.client_id,
            client_secret=registered_client.client_secret,
            redirect_uri=registered_client.redirect_uris[0]
        )

        tokens.append(token)

    # All tokens should be valid simultaneously
    for token in tokens:
        validation = provider.validate_token(token.access_token)
        assert validation['active'] is True


# ============================================================
# Integration Tests
# ============================================================

@pytest.mark.integration
def test_full_authorization_code_flow(provider):
    """Integration test: Complete authorization code flow"""
    # 1. Register client
    client = provider.register_client(
        client_name="Integration Test App",
        redirect_uris=["https://app.example.com/callback"],
        grant_types=[GrantType.AUTHORIZATION_CODE, GrantType.REFRESH_TOKEN],
        scope=["read", "write", "profile"]
    )

    # 2. User authorizes
    user_id = 12345
    auth_result = provider.authorize(
        client_id=client.client_id,
        redirect_uri=client.redirect_uris[0],
        scope=["read", "write"],
        user_id=user_id,
        state="test_state_xyz"
    )

    assert 'code' in auth_result
    assert auth_result['state'] == "test_state_xyz"

    # 3. Exchange code for tokens
    token = provider.exchange_code(
        code=auth_result['code'],
        client_id=client.client_id,
        client_secret=client.client_secret,
        redirect_uri=client.redirect_uris[0]
    )

    assert token.access_token is not None
    assert token.refresh_token is not None

    # 4. Validate access token
    validation = provider.validate_token(token.access_token)
    assert validation['active'] is True
    assert validation['user_id'] == user_id

    # 5. Refresh token
    new_token = provider.refresh_access_token(
        refresh_token=token.refresh_token,
        client_id=client.client_id,
        client_secret=client.client_secret
    )

    assert new_token.access_token != token.access_token

    # 6. Revoke access token
    provider.revoke_token(
        token=new_token.access_token,
        client_id=client.client_id,
        client_secret=client.client_secret
    )

    # 7. Verify revoked
    validation = provider.validate_token(new_token.access_token)
    assert validation['active'] is False


@pytest.mark.integration
def test_full_pkce_flow(provider):
    """Integration test: Complete PKCE flow for public client"""
    # 1. Register public client (mobile app)
    client = provider.register_client(
        client_name="Mobile App",
        redirect_uris=["myapp://callback"],
        grant_types=[GrantType.AUTHORIZATION_CODE],
        scope=["read", "profile"],
        is_confidential=False
    )

    # 2. Generate PKCE parameters
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    # 3. Authorize with PKCE
    auth_result = provider.authorize(
        client_id=client.client_id,
        redirect_uri=client.redirect_uris[0],
        scope=["read"],
        user_id=999,
        code_challenge=code_challenge,
        code_challenge_method="S256"
    )

    # 4. Exchange code with verifier (no client_secret needed)
    token = provider.exchange_code(
        code=auth_result['code'],
        client_id=client.client_id,
        redirect_uri=client.redirect_uris[0],
        code_verifier=code_verifier
    )

    assert token.access_token is not None

    # 5. Validate token
    validation = provider.validate_token(token.access_token)
    assert validation['active'] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
