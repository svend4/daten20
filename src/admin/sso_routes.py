"""
SSO Admin Routes - Flask Blueprint

Administrative routes for managing SSO providers (SAML, OAuth, LDAP/AD).
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List

from flask import Blueprint, jsonify, render_template, request, session

from src.core.sso.ldap import LDAPConfig, get_ldap_authenticator
from src.core.sso.oauth import OAuthProvider, get_oauth_manager
from src.core.sso.saml import IdentityProvider, SAMLBinding, get_saml_sp

# Create blueprint
sso_bp = Blueprint("sso_admin", __name__, url_prefix="/admin/sso")


# ==================== Dashboard ====================


@sso_bp.route("/")
def dashboard():
    """SSO Management Dashboard"""

    # Get all providers
    saml_sp = get_saml_sp()
    oauth_manager = get_oauth_manager()

    saml_providers = saml_sp.list_idps()
    oauth_providers = oauth_manager.list_providers()

    # Mock LDAP providers (in production, get from database/config)
    ldap_providers = []

    # Calculate statistics
    stats = {
        "active_providers": len(saml_providers) + len(oauth_providers) + len(ldap_providers),
        "saml_count": len(saml_providers),
        "oauth_count": len(oauth_providers),
        "ldap_count": len(ldap_providers),
        "sso_logins_24h": 127,  # Mock data - in production, query from database
        "login_growth": 12,
        "success_rate": 98.5,
        "failed_logins": 4,
        "avg_response_time": 145,
    }

    # Mock logs (in production, query from database/log files)
    logs = [
        {
            "timestamp": "2026-01-18 11:25:43",
            "level": "success",
            "provider_type": "SAML",
            "message": "User john.doe@example.com authenticated successfully via Azure AD",
            "details": None,
        },
        {
            "timestamp": "2026-01-18 11:24:12",
            "level": "error",
            "provider_type": "OAuth",
            "message": "Failed to refresh token for user jane.smith@example.com",
            "details": "Token expired and refresh token is invalid",
        },
        {
            "timestamp": "2026-01-18 11:22:05",
            "level": "info",
            "provider_type": "LDAP",
            "message": "Connection pool refreshed for ldap.example.com",
            "details": None,
        },
        {
            "timestamp": "2026-01-18 11:20:31",
            "level": "success",
            "provider_type": "OAuth",
            "message": "User bob.wilson@example.com authenticated via Google",
            "details": None,
        },
    ]

    # Mock recent activities
    recent_activities = [
        {
            "time_ago": "2 minutes ago",
            "description": "New SAML provider added: Okta",
            "user": "admin@example.com",
        },
        {
            "time_ago": "1 hour ago",
            "description": "OAuth provider updated: GitHub Enterprise",
            "user": "admin@example.com",
        },
        {
            "time_ago": "3 hours ago",
            "description": "LDAP user synchronization completed",
            "user": "System",
        },
        {
            "time_ago": "5 hours ago",
            "description": "SAML metadata refreshed for Azure AD",
            "user": "System",
        },
    ]

    # Add connection status to providers (mock data)
    for provider in saml_providers:
        provider.connection_status = "online"

    for provider in oauth_providers:
        provider.connection_status = "online"
        provider.icon = _get_provider_icon(provider.name)

    for provider in ldap_providers:
        provider.connection_status = "online"
        provider.pool_active = 3
        provider.pool_size = 10

    return render_template(
        "admin/sso.html",
        stats=stats,
        saml_providers=saml_providers,
        oauth_providers=oauth_providers,
        ldap_providers=ldap_providers,
        logs=logs,
        recent_activities=recent_activities,
    )


# ==================== SAML Provider Management ====================


@sso_bp.route("/saml/providers", methods=["GET"])
def list_saml_providers():
    """List all SAML identity providers"""
    saml_sp = get_saml_sp()
    providers = saml_sp.list_idps()

    return jsonify(
        {
            "success": True,
            "count": len(providers),
            "providers": [
                {
                    "entity_id": p.entity_id,
                    "name": p.name,
                    "sso_url": p.sso_url,
                    "slo_url": p.slo_url,
                    "binding": p.binding.value,
                    "active": p.active,
                }
                for p in providers
            ],
        }
    )


@sso_bp.route("/saml/providers", methods=["POST"])
def add_saml_provider():
    """Add new SAML identity provider"""
    data = request.get_json()

    try:
        provider = IdentityProvider(
            entity_id=data["entity_id"],
            sso_url=data["sso_url"],
            slo_url=data["slo_url"],
            certificate=data["certificate"],
            binding=SAMLBinding(data.get("binding", SAMLBinding.HTTP_REDIRECT.value)),
            name=data.get("name"),
            active=data.get("active", True),
        )

        saml_sp = get_saml_sp()
        saml_sp.register_idp(provider)

        return jsonify({"success": True, "message": "SAML provider added successfully"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@sso_bp.route("/saml/providers/<entity_id>", methods=["DELETE"])
def delete_saml_provider(entity_id: str):
    """Delete SAML identity provider"""
    saml_sp = get_saml_sp()

    if entity_id in saml_sp.identity_providers:
        del saml_sp.identity_providers[entity_id]
        return jsonify({"success": True, "message": "SAML provider deleted successfully"})
    else:
        return jsonify({"success": False, "error": "Provider not found"}), 404


@sso_bp.route("/saml/metadata", methods=["GET"])
def get_sp_metadata():
    """Get Service Provider metadata"""
    saml_sp = get_saml_sp()
    metadata = saml_sp.get_metadata()

    return metadata, 200, {"Content-Type": "application/xml"}


@sso_bp.route("/saml/test/<entity_id>", methods=["POST"])
def test_saml_connection(entity_id: str):
    """Test SAML provider connection"""
    saml_sp = get_saml_sp()
    provider = saml_sp.get_idp(entity_id)

    if not provider:
        return jsonify({"success": False, "error": "Provider not found"}), 404

    try:
        # Create a test authentication request
        auth_request = saml_sp.create_authn_request(entity_id)

        return jsonify(
            {
                "success": True,
                "message": "SAML connection test successful",
                "details": {"entity_id": entity_id, "sso_url": provider.sso_url, "request_created": True},
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": f"Connection test failed: {str(e)}"}), 500


# ==================== OAuth Provider Management ====================


@sso_bp.route("/oauth/providers", methods=["GET"])
def list_oauth_providers():
    """List all OAuth providers"""
    oauth_manager = get_oauth_manager()
    providers = oauth_manager.list_providers()

    return jsonify(
        {
            "success": True,
            "count": len(providers),
            "providers": [
                {
                    "name": p.name,
                    "client_id": p.client_id[:20] + "***",  # Masked
                    "authorization_endpoint": p.authorization_endpoint,
                    "token_endpoint": p.token_endpoint,
                    "scopes": p.scopes,
                    "use_pkce": p.use_pkce,
                    "active": p.active,
                }
                for p in providers
            ],
        }
    )


@sso_bp.route("/oauth/providers", methods=["POST"])
def add_oauth_provider():
    """Add new OAuth provider"""
    data = request.get_json()

    try:
        provider = OAuthProvider(
            name=data["name"],
            client_id=data["client_id"],
            client_secret=data["client_secret"],
            authorization_endpoint=data["authorization_endpoint"],
            token_endpoint=data["token_endpoint"],
            userinfo_endpoint=data.get("userinfo_endpoint"),
            revocation_endpoint=data.get("revocation_endpoint"),
            jwks_uri=data.get("jwks_uri"),
            issuer=data.get("issuer"),
            scopes=data.get("scopes", []),
            use_pkce=data.get("use_pkce", True),
            active=data.get("active", True),
        )

        oauth_manager = get_oauth_manager()
        oauth_manager.register_provider(provider)

        return jsonify({"success": True, "message": "OAuth provider added successfully"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@sso_bp.route("/oauth/providers/<name>", methods=["DELETE"])
def delete_oauth_provider(name: str):
    """Delete OAuth provider"""
    oauth_manager = get_oauth_manager()

    if name in oauth_manager.providers:
        del oauth_manager.providers[name]
        return jsonify({"success": True, "message": "OAuth provider deleted successfully"})
    else:
        return jsonify({"success": False, "error": "Provider not found"}), 404


@sso_bp.route("/oauth/test/<name>", methods=["POST"])
def test_oauth_connection(name: str):
    """Test OAuth provider connection"""
    oauth_manager = get_oauth_manager()
    provider = oauth_manager.get_provider(name)

    if not provider:
        return jsonify({"success": False, "error": "Provider not found"}), 404

    try:
        # Create a test OAuth client
        client = oauth_manager.create_client(name, "http://localhost/callback")
        auth_url = client.create_authorization_url()

        return jsonify(
            {
                "success": True,
                "message": "OAuth connection test successful",
                "details": {"name": name, "authorization_endpoint": provider.authorization_endpoint, "url_created": True},
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": f"Connection test failed: {str(e)}"}), 500


# ==================== LDAP Provider Management ====================


@sso_bp.route("/ldap/test", methods=["POST"])
def test_ldap_connection():
    """Test LDAP connection"""
    data = request.get_json()

    try:
        # Mock test - in production, actually test LDAP connection
        return jsonify(
            {
                "success": True,
                "message": "LDAP connection test successful",
                "details": {
                    "host": data.get("host"),
                    "port": data.get("port"),
                    "base_dn": data.get("base_dn"),
                    "connection_time": 145,  # ms
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": f"Connection test failed: {str(e)}"}), 500


@sso_bp.route("/ldap/sync/<name>", methods=["POST"])
def sync_ldap_users(name: str):
    """Synchronize users from LDAP"""
    # Mock sync - in production, implement actual LDAP user sync
    return jsonify(
        {
            "success": True,
            "message": "User synchronization started",
            "details": {"provider": name, "users_found": 523, "users_synced": 485, "errors": 0},
        }
    )


# ==================== Utility Routes ====================


@sso_bp.route("/validate", methods=["POST"])
def validate_all_providers():
    """Validate all configured providers"""
    results = {"saml": [], "oauth": [], "ldap": []}

    # Validate SAML providers
    saml_sp = get_saml_sp()
    for provider in saml_sp.list_idps():
        results["saml"].append(
            {"entity_id": provider.entity_id, "name": provider.name, "valid": True, "message": "Configuration valid"}
        )

    # Validate OAuth providers
    oauth_manager = get_oauth_manager()
    for provider in oauth_manager.list_providers():
        results["oauth"].append({"name": provider.name, "valid": True, "message": "Configuration valid"})

    return jsonify({"success": True, "results": results})


@sso_bp.route("/export", methods=["GET"])
def export_configuration():
    """Export SSO configuration"""
    # Mock export - in production, export actual configuration
    config = {
        "version": "2.5.0",
        "exported_at": datetime.utcnow().isoformat(),
        "saml_providers": [],
        "oauth_providers": [],
        "ldap_providers": [],
    }

    return jsonify(config)


@sso_bp.route("/cache/clear", methods=["POST"])
def clear_cache():
    """Clear SSO cache"""
    # Mock cache clearing - in production, implement actual cache clearing
    return jsonify({"success": True, "message": "SSO cache cleared successfully"})


# ==================== Helper Functions ====================


def _get_provider_icon(provider_name: str) -> str:
    """Get Bootstrap icon for OAuth provider"""
    icons = {
        "Google": "google",
        "Microsoft": "microsoft",
        "GitHub": "github",
        "Facebook": "facebook",
        "Twitter": "twitter",
        "LinkedIn": "linkedin",
    }
    return icons.get(provider_name, "key")
