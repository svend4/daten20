"""
Admin Module - Administrative interfaces and routes

Provides administrative functionality for the DMS including SSO management,
user administration, system settings, and monitoring tools.
"""

from .sso_routes import sso_bp

__all__ = ["sso_bp"]
