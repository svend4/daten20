"""
SSO SAML 2.0 Integration

Provides SAML-based Single Sign-On authentication.
"""

import base64
import hashlib
import uuid
import xml.etree.ElementTree as ET
import zlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlencode


class SAMLBinding(str, Enum):
    """SAML binding types"""

    HTTP_REDIRECT = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    HTTP_POST = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
    HTTP_ARTIFACT = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Artifact"


class SAMLNameIDFormat(str, Enum):
    """Name ID format types"""

    PERSISTENT = "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent"
    TRANSIENT = "urn:oasis:names:tc:SAML:2.0:nameid-format:transient"
    EMAIL = "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
    UNSPECIFIED = "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified"


@dataclass
class SAMLConfig:
    """SAML Service Provider configuration"""

    entity_id: str
    acs_url: str  # Assertion Consumer Service URL
    slo_url: str  # Single Logout URL
    certificate: Optional[str] = None
    private_key: Optional[str] = None
    name_id_format: SAMLNameIDFormat = SAMLNameIDFormat.PERSISTENT
    want_assertions_signed: bool = True
    want_response_signed: bool = True


@dataclass
class IdentityProvider:
    """Identity Provider configuration"""

    entity_id: str
    sso_url: str
    slo_url: str
    certificate: str
    binding: SAMLBinding = SAMLBinding.HTTP_REDIRECT
    name: Optional[str] = None
    active: bool = True


@dataclass
class SAMLResponse:
    """Parsed SAML response"""

    name_id: str
    session_index: str
    attributes: Dict[str, Any]
    issuer: str
    not_on_or_after: datetime
    audience: str
    subject_confirmation_data: Dict[str, Any]


class SAMLServiceProvider:
    """SAML Service Provider implementation"""

    def __init__(self, config: SAMLConfig):
        self.config = config
        self.identity_providers: Dict[str, IdentityProvider] = {}

    def register_idp(self, idp: IdentityProvider):
        """Register an Identity Provider"""
        self.identity_providers[idp.entity_id] = idp

    def get_idp(self, entity_id: str) -> Optional[IdentityProvider]:
        """Get Identity Provider by entity ID"""
        return self.identity_providers.get(entity_id)

    def list_idps(self) -> list[IdentityProvider]:
        """List all registered Identity Providers"""
        return [idp for idp in self.identity_providers.values() if idp.active]

    def create_authn_request(self, idp_entity_id: str, relay_state: Optional[str] = None) -> Dict[str, str]:
        """Create SAML Authentication Request"""
        idp = self.get_idp(idp_entity_id)
        if not idp:
            raise ValueError(f"Identity Provider not found: {idp_entity_id}")

        request_id = f"_{uuid.uuid4()}"
        issue_instant = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        # Build SAML AuthnRequest XML
        authn_request = f"""<?xml version="1.0" encoding="UTF-8"?>
<samlp:AuthnRequest
    xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
    ID="{request_id}"
    Version="2.0"
    IssueInstant="{issue_instant}"
    Destination="{idp.sso_url}"
    AssertionConsumerServiceURL="{self.config.acs_url}"
    ProtocolBinding="{SAMLBinding.HTTP_POST.value}">
    <saml:Issuer>{self.config.entity_id}</saml:Issuer>
    <samlp:NameIDPolicy
        Format="{self.config.name_id_format.value}"
        AllowCreate="true"/>
</samlp:AuthnRequest>"""

        if idp.binding == SAMLBinding.HTTP_REDIRECT:
            # Deflate and base64 encode for HTTP-Redirect
            deflated = zlib.compress(authn_request.encode("utf-8"))[2:-4]
            encoded = base64.b64encode(deflated).decode("utf-8")

            params = {"SAMLRequest": encoded}
            if relay_state:
                params["RelayState"] = relay_state

            redirect_url = f"{idp.sso_url}?{urlencode(params)}"

            return {"type": "redirect", "url": redirect_url, "request_id": request_id}
        else:
            # Base64 encode for HTTP-POST
            encoded = base64.b64encode(authn_request.encode("utf-8")).decode("utf-8")

            return {
                "type": "post",
                "url": idp.sso_url,
                "saml_request": encoded,
                "relay_state": relay_state or "",
                "request_id": request_id,
            }

    def parse_response(self, saml_response: str) -> SAMLResponse:
        """Parse and validate SAML Response"""
        try:
            # Decode base64
            decoded = base64.b64decode(saml_response)

            # Parse XML
            root = ET.fromstring(decoded)

            # Define namespaces
            ns = {"samlp": "urn:oasis:names:tc:SAML:2.0:protocol", "saml": "urn:oasis:names:tc:SAML:2.0:assertion"}

            # Extract Issuer
            issuer_elem = root.find(".//saml:Issuer", ns)
            issuer = issuer_elem.text if issuer_elem is not None else ""

            # Extract Assertion
            assertion = root.find(".//saml:Assertion", ns)
            if assertion is None:
                raise ValueError("No Assertion found in SAML Response")

            # Extract Subject
            subject = assertion.find(".//saml:Subject", ns)
            name_id_elem = subject.find(".//saml:NameID", ns)
            name_id = name_id_elem.text if name_id_elem is not None else ""

            # Extract SessionIndex
            authn_statement = assertion.find(".//saml:AuthnStatement", ns)
            session_index = authn_statement.get("SessionIndex", "") if authn_statement is not None else ""

            # Extract Attributes
            attributes = {}
            attr_statements = assertion.findall(".//saml:AttributeStatement", ns)
            for attr_statement in attr_statements:
                attrs = attr_statement.findall(".//saml:Attribute", ns)
                for attr in attrs:
                    attr_name = attr.get("Name", "")
                    attr_values = attr.findall(".//saml:AttributeValue", ns)
                    if len(attr_values) == 1:
                        attributes[attr_name] = attr_values[0].text
                    else:
                        attributes[attr_name] = [av.text for av in attr_values]

            # Extract Conditions
            conditions = assertion.find(".//saml:Conditions", ns)
            not_on_or_after_str = conditions.get("NotOnOrAfter", "") if conditions is not None else ""
            not_on_or_after = datetime.strptime(not_on_or_after_str, "%Y-%m-%dT%H:%M:%SZ")

            # Extract Audience
            audience_elem = conditions.find(".//saml:Audience", ns) if conditions is not None else None
            audience = audience_elem.text if audience_elem is not None else ""

            # Validate audience
            if audience != self.config.entity_id:
                raise ValueError(f"Invalid audience: {audience}")

            # Validate timestamp
            if datetime.utcnow() > not_on_or_after:
                raise ValueError("SAML Response has expired")

            return SAMLResponse(
                name_id=name_id,
                session_index=session_index,
                attributes=attributes,
                issuer=issuer,
                not_on_or_after=not_on_or_after,
                audience=audience,
                subject_confirmation_data={},
            )

        except ET.ParseError as e:
            raise ValueError(f"Failed to parse SAML Response: {e}")

    def create_logout_request(self, idp_entity_id: str, name_id: str, session_index: str) -> Dict[str, str]:
        """Create SAML Logout Request"""
        idp = self.get_idp(idp_entity_id)
        if not idp:
            raise ValueError(f"Identity Provider not found: {idp_entity_id}")

        request_id = f"_{uuid.uuid4()}"
        issue_instant = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        logout_request = f"""<?xml version="1.0" encoding="UTF-8"?>
<samlp:LogoutRequest
    xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
    ID="{request_id}"
    Version="2.0"
    IssueInstant="{issue_instant}"
    Destination="{idp.slo_url}">
    <saml:Issuer>{self.config.entity_id}</saml:Issuer>
    <saml:NameID Format="{self.config.name_id_format.value}">{name_id}</saml:NameID>
    <samlp:SessionIndex>{session_index}</samlp:SessionIndex>
</samlp:LogoutRequest>"""

        # Deflate and base64 encode
        deflated = zlib.compress(logout_request.encode("utf-8"))[2:-4]
        encoded = base64.b64encode(deflated).decode("utf-8")

        params = {"SAMLRequest": encoded}
        redirect_url = f"{idp.slo_url}?{urlencode(params)}"

        return {"type": "redirect", "url": redirect_url, "request_id": request_id}

    def get_metadata(self) -> str:
        """Generate SP metadata XML"""
        valid_until = (datetime.utcnow() + timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")

        metadata = f"""<?xml version="1.0" encoding="UTF-8"?>
<md:EntityDescriptor
    xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
    xmlns:ds="http://www.w3.org/2000/09/xmldsig#"
    entityID="{self.config.entity_id}"
    validUntil="{valid_until}">
    <md:SPSSODescriptor
        AuthnRequestsSigned="false"
        WantAssertionsSigned="{str(self.config.want_assertions_signed).lower()}"
        protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
        <md:NameIDFormat>{self.config.name_id_format.value}</md:NameIDFormat>
        <md:AssertionConsumerService
            Binding="{SAMLBinding.HTTP_POST.value}"
            Location="{self.config.acs_url}"
            index="0"
            isDefault="true"/>
        <md:SingleLogoutService
            Binding="{SAMLBinding.HTTP_REDIRECT.value}"
            Location="{self.config.slo_url}"/>
    </md:SPSSODescriptor>
</md:EntityDescriptor>"""

        return metadata

    def map_attributes_to_user(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Map SAML attributes to user fields"""
        # Common attribute mappings
        attr_map = {
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress": "email",
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname": "first_name",
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname": "last_name",
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name": "full_name",
            "email": "email",
            "givenName": "first_name",
            "sn": "last_name",
            "displayName": "full_name",
            "uid": "username",
            "groups": "groups",
            "role": "role",
        }

        user_data = {}
        for saml_attr, user_attr in attr_map.items():
            if saml_attr in attributes:
                user_data[user_attr] = attributes[saml_attr]

        return user_data


# Global instance
_saml_sp: Optional[SAMLServiceProvider] = None


def get_saml_sp() -> SAMLServiceProvider:
    """Get global SAML Service Provider instance"""
    global _saml_sp

    if _saml_sp is None:
        # Default configuration
        config = SAMLConfig(
            entity_id="https://dms.example.com/saml/metadata",
            acs_url="https://dms.example.com/saml/acs",
            slo_url="https://dms.example.com/saml/slo",
        )
        _saml_sp = SAMLServiceProvider(config)

    return _saml_sp


def configure_saml_sp(config: SAMLConfig):
    """Configure SAML Service Provider"""
    global _saml_sp
    _saml_sp = SAMLServiceProvider(config)
