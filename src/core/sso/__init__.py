"""
SSO (Single Sign-On) Integration Module

Provides SAML 2.0, OAuth 2.0, OpenID Connect, and LDAP/AD authentication.
"""

from src.core.sso.ldap import (
    ActiveDirectoryAuthenticator,
    ADConfig,
    GroupMapping,
    LDAPAuthenticator,
    LDAPAuthMethod,
    LDAPConfig,
    LDAPConnection,
    LDAPGroup,
    LDAPScope,
    LDAPUser,
    UserMapping,
    configure_ldap_authenticator,
    get_ldap_authenticator,
)
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
from src.core.sso.saml import (
    IdentityProvider,
    SAMLBinding,
    SAMLConfig,
    SAMLNameIDFormat,
    SAMLResponse,
    SAMLServiceProvider,
    configure_saml_sp,
    get_saml_sp,
)

__all__ = [
    # SAML
    "SAMLBinding",
    "SAMLNameIDFormat",
    "SAMLConfig",
    "IdentityProvider",
    "SAMLResponse",
    "SAMLServiceProvider",
    "get_saml_sp",
    "configure_saml_sp",
    # OAuth
    "OAuthGrantType",
    "OAuthResponseType",
    "OAuthTokenType",
    "OAuthScope",
    "OAuthProvider",
    "OAuthState",
    "OAuthToken",
    "UserInfo",
    "OAuthClient",
    "OAuthManager",
    "GOOGLE_PROVIDER",
    "MICROSOFT_PROVIDER",
    "GITHUB_PROVIDER",
    "get_oauth_manager",
    "configure_oauth_manager",
    # LDAP
    "LDAPAuthMethod",
    "LDAPScope",
    "LDAPConfig",
    "ADConfig",
    "UserMapping",
    "GroupMapping",
    "LDAPUser",
    "LDAPGroup",
    "LDAPConnection",
    "LDAPAuthenticator",
    "ActiveDirectoryAuthenticator",
    "get_ldap_authenticator",
    "configure_ldap_authenticator",
]
