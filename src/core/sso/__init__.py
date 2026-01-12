"""
SSO (Single Sign-On) Integration Module

Provides SAML 2.0, OAuth 2.0, OpenID Connect, and LDAP/AD authentication.
"""

from src.core.sso.saml import (
    SAMLBinding,
    SAMLNameIDFormat,
    SAMLConfig,
    IdentityProvider,
    SAMLResponse,
    SAMLServiceProvider,
    get_saml_sp,
    configure_saml_sp,
)

from src.core.sso.oauth import (
    OAuthGrantType,
    OAuthResponseType,
    OAuthTokenType,
    OAuthScope,
    OAuthProvider,
    OAuthState,
    OAuthToken,
    UserInfo,
    OAuthClient,
    OAuthManager,
    GOOGLE_PROVIDER,
    MICROSOFT_PROVIDER,
    GITHUB_PROVIDER,
    get_oauth_manager,
    configure_oauth_manager,
)

from src.core.sso.ldap import (
    LDAPAuthMethod,
    LDAPScope,
    LDAPConfig,
    ADConfig,
    UserMapping,
    GroupMapping,
    LDAPUser,
    LDAPGroup,
    LDAPConnection,
    LDAPAuthenticator,
    ActiveDirectoryAuthenticator,
    get_ldap_authenticator,
    configure_ldap_authenticator,
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
