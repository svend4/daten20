"""Comprehensive tests for SAML SSO module"""

import base64
import uuid
import xml.etree.ElementTree as ET
import zlib
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

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


class TestSAMLBinding:
    """Test SAMLBinding enum"""

    def test_http_redirect_binding(self):
        """Test HTTP-Redirect binding value"""
        assert SAMLBinding.HTTP_REDIRECT == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"

    def test_http_post_binding(self):
        """Test HTTP-POST binding value"""
        assert SAMLBinding.HTTP_POST == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"

    def test_http_artifact_binding(self):
        """Test HTTP-Artifact binding value"""
        assert SAMLBinding.HTTP_ARTIFACT == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Artifact"


class TestSAMLNameIDFormat:
    """Test SAMLNameIDFormat enum"""

    def test_persistent_format(self):
        """Test persistent name ID format"""
        assert SAMLNameIDFormat.PERSISTENT == "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent"

    def test_transient_format(self):
        """Test transient name ID format"""
        assert SAMLNameIDFormat.TRANSIENT == "urn:oasis:names:tc:SAML:2.0:nameid-format:transient"

    def test_email_format(self):
        """Test email name ID format"""
        assert SAMLNameIDFormat.EMAIL == "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"

    def test_unspecified_format(self):
        """Test unspecified name ID format"""
        assert SAMLNameIDFormat.UNSPECIFIED == "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified"


class TestSAMLConfig:
    """Test SAMLConfig dataclass"""

    def test_config_creation_minimal(self):
        """Test creating SAMLConfig with minimal parameters"""
        config = SAMLConfig(
            entity_id="https://sp.example.com/metadata",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        assert config.entity_id == "https://sp.example.com/metadata"
        assert config.acs_url == "https://sp.example.com/acs"
        assert config.slo_url == "https://sp.example.com/slo"

    def test_config_default_values(self):
        """Test SAMLConfig default values"""
        config = SAMLConfig(
            entity_id="https://sp.example.com/metadata",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        assert config.certificate is None
        assert config.private_key is None
        assert config.name_id_format == SAMLNameIDFormat.PERSISTENT
        assert config.want_assertions_signed is True
        assert config.want_response_signed is True

    def test_config_with_certificate(self):
        """Test SAMLConfig with certificate and private key"""
        config = SAMLConfig(
            entity_id="https://sp.example.com/metadata",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
            certificate="CERT_DATA",
            private_key="KEY_DATA",
        )
        assert config.certificate == "CERT_DATA"
        assert config.private_key == "KEY_DATA"

    def test_config_custom_name_id_format(self):
        """Test SAMLConfig with custom name ID format"""
        config = SAMLConfig(
            entity_id="https://sp.example.com/metadata",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
            name_id_format=SAMLNameIDFormat.EMAIL,
        )
        assert config.name_id_format == SAMLNameIDFormat.EMAIL

    def test_config_signing_requirements(self):
        """Test SAMLConfig signing requirements"""
        config = SAMLConfig(
            entity_id="https://sp.example.com/metadata",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
            want_assertions_signed=False,
            want_response_signed=False,
        )
        assert config.want_assertions_signed is False
        assert config.want_response_signed is False


class TestIdentityProvider:
    """Test IdentityProvider dataclass"""

    def test_idp_creation_minimal(self):
        """Test creating IdentityProvider with minimal parameters"""
        idp = IdentityProvider(
            entity_id="https://idp.example.com",
            sso_url="https://idp.example.com/sso",
            slo_url="https://idp.example.com/slo",
            certificate="IDP_CERT",
        )
        assert idp.entity_id == "https://idp.example.com"
        assert idp.sso_url == "https://idp.example.com/sso"
        assert idp.slo_url == "https://idp.example.com/slo"
        assert idp.certificate == "IDP_CERT"

    def test_idp_default_values(self):
        """Test IdentityProvider default values"""
        idp = IdentityProvider(
            entity_id="https://idp.example.com",
            sso_url="https://idp.example.com/sso",
            slo_url="https://idp.example.com/slo",
            certificate="IDP_CERT",
        )
        assert idp.binding == SAMLBinding.HTTP_REDIRECT
        assert idp.name is None
        assert idp.active is True

    def test_idp_with_name(self):
        """Test IdentityProvider with custom name"""
        idp = IdentityProvider(
            entity_id="https://idp.example.com",
            sso_url="https://idp.example.com/sso",
            slo_url="https://idp.example.com/slo",
            certificate="IDP_CERT",
            name="Example IDP",
        )
        assert idp.name == "Example IDP"

    def test_idp_custom_binding(self):
        """Test IdentityProvider with custom binding"""
        idp = IdentityProvider(
            entity_id="https://idp.example.com",
            sso_url="https://idp.example.com/sso",
            slo_url="https://idp.example.com/slo",
            certificate="IDP_CERT",
            binding=SAMLBinding.HTTP_POST,
        )
        assert idp.binding == SAMLBinding.HTTP_POST

    def test_idp_inactive(self):
        """Test IdentityProvider with active=False"""
        idp = IdentityProvider(
            entity_id="https://idp.example.com",
            sso_url="https://idp.example.com/sso",
            slo_url="https://idp.example.com/slo",
            certificate="IDP_CERT",
            active=False,
        )
        assert idp.active is False


class TestSAMLResponse:
    """Test SAMLResponse dataclass"""

    def test_saml_response_creation(self):
        """Test creating SAMLResponse"""
        not_on_or_after = datetime.utcnow() + timedelta(hours=1)
        response = SAMLResponse(
            name_id="user@example.com",
            session_index="session123",
            attributes={"email": "user@example.com"},
            issuer="https://idp.example.com",
            not_on_or_after=not_on_or_after,
            audience="https://sp.example.com",
            subject_confirmation_data={},
        )
        assert response.name_id == "user@example.com"
        assert response.session_index == "session123"
        assert response.attributes == {"email": "user@example.com"}

    def test_saml_response_with_multiple_attributes(self):
        """Test SAMLResponse with multiple attributes"""
        response = SAMLResponse(
            name_id="user@example.com",
            session_index="session123",
            attributes={
                "email": "user@example.com",
                "firstName": "John",
                "lastName": "Doe",
                "groups": ["admin", "users"],
            },
            issuer="https://idp.example.com",
            not_on_or_after=datetime.utcnow() + timedelta(hours=1),
            audience="https://sp.example.com",
            subject_confirmation_data={},
        )
        assert response.attributes["email"] == "user@example.com"
        assert response.attributes["groups"] == ["admin", "users"]

    def test_saml_response_timestamps(self):
        """Test SAMLResponse timestamp handling"""
        not_on_or_after = datetime(2025, 12, 31, 23, 59, 59)
        response = SAMLResponse(
            name_id="user@example.com",
            session_index="session123",
            attributes={},
            issuer="https://idp.example.com",
            not_on_or_after=not_on_or_after,
            audience="https://sp.example.com",
            subject_confirmation_data={},
        )
        assert response.not_on_or_after == not_on_or_after


class TestSAMLServiceProviderInit:
    """Test SAMLServiceProvider initialization"""

    def test_sp_initialization(self):
        """Test ServiceProvider initialization"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)
        assert sp.config == config
        assert sp.identity_providers == {}

    def test_sp_stores_config(self):
        """Test ServiceProvider stores configuration"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)
        assert sp.config.entity_id == "https://sp.example.com"
        assert sp.config.acs_url == "https://sp.example.com/acs"


class TestRegisterIDP:
    """Test register_idp method"""

    def test_register_single_idp(self):
        """Test registering single IDP"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        idp = IdentityProvider(
            entity_id="https://idp1.example.com",
            sso_url="https://idp1.example.com/sso",
            slo_url="https://idp1.example.com/slo",
            certificate="CERT1",
        )
        sp.register_idp(idp)

        assert len(sp.identity_providers) == 1
        assert "https://idp1.example.com" in sp.identity_providers

    def test_register_multiple_idps(self):
        """Test registering multiple IDPs"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        idp1 = IdentityProvider(
            entity_id="https://idp1.example.com",
            sso_url="https://idp1.example.com/sso",
            slo_url="https://idp1.example.com/slo",
            certificate="CERT1",
        )
        idp2 = IdentityProvider(
            entity_id="https://idp2.example.com",
            sso_url="https://idp2.example.com/sso",
            slo_url="https://idp2.example.com/slo",
            certificate="CERT2",
        )

        sp.register_idp(idp1)
        sp.register_idp(idp2)

        assert len(sp.identity_providers) == 2

    def test_register_idp_overwrite(self):
        """Test registering IDP with same entity_id overwrites"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        idp1 = IdentityProvider(
            entity_id="https://idp.example.com",
            sso_url="https://idp.example.com/sso",
            slo_url="https://idp.example.com/slo",
            certificate="CERT1",
        )
        idp2 = IdentityProvider(
            entity_id="https://idp.example.com",
            sso_url="https://idp.example.com/sso2",
            slo_url="https://idp.example.com/slo2",
            certificate="CERT2",
        )

        sp.register_idp(idp1)
        sp.register_idp(idp2)

        assert len(sp.identity_providers) == 1
        assert sp.identity_providers["https://idp.example.com"].certificate == "CERT2"


class TestGetIDP:
    """Test get_idp method"""

    def test_get_existing_idp(self):
        """Test getting existing IDP"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        idp = IdentityProvider(
            entity_id="https://idp.example.com",
            sso_url="https://idp.example.com/sso",
            slo_url="https://idp.example.com/slo",
            certificate="CERT",
        )
        sp.register_idp(idp)

        retrieved = sp.get_idp("https://idp.example.com")
        assert retrieved == idp

    def test_get_nonexistent_idp(self):
        """Test getting non-existent IDP returns None"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        retrieved = sp.get_idp("https://nonexistent.example.com")
        assert retrieved is None


class TestListIDPs:
    """Test list_idps method"""

    def test_list_empty_idps(self):
        """Test listing IDPs when none registered"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        idps = sp.list_idps()
        assert idps == []

    def test_list_active_idps(self):
        """Test listing only active IDPs"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        idp1 = IdentityProvider(
            entity_id="https://idp1.example.com",
            sso_url="https://idp1.example.com/sso",
            slo_url="https://idp1.example.com/slo",
            certificate="CERT1",
            active=True,
        )
        idp2 = IdentityProvider(
            entity_id="https://idp2.example.com",
            sso_url="https://idp2.example.com/sso",
            slo_url="https://idp2.example.com/slo",
            certificate="CERT2",
            active=False,
        )

        sp.register_idp(idp1)
        sp.register_idp(idp2)

        idps = sp.list_idps()
        assert len(idps) == 1
        assert idps[0].entity_id == "https://idp1.example.com"

    def test_list_multiple_active_idps(self):
        """Test listing multiple active IDPs"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        idp1 = IdentityProvider(
            entity_id="https://idp1.example.com",
            sso_url="https://idp1.example.com/sso",
            slo_url="https://idp1.example.com/slo",
            certificate="CERT1",
        )
        idp2 = IdentityProvider(
            entity_id="https://idp2.example.com",
            sso_url="https://idp2.example.com/sso",
            slo_url="https://idp2.example.com/slo",
            certificate="CERT2",
        )

        sp.register_idp(idp1)
        sp.register_idp(idp2)

        idps = sp.list_idps()
        assert len(idps) == 2


class TestCreateAuthnRequest:
    """Test create_authn_request method"""

    def test_create_authn_request_http_redirect(self):
        """Test creating authn request with HTTP-Redirect binding"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        idp = IdentityProvider(
            entity_id="https://idp.example.com",
            sso_url="https://idp.example.com/sso",
            slo_url="https://idp.example.com/slo",
            certificate="CERT",
            binding=SAMLBinding.HTTP_REDIRECT,
        )
        sp.register_idp(idp)

        result = sp.create_authn_request("https://idp.example.com")

        assert result["type"] == "redirect"
        assert "url" in result
        assert "request_id" in result
        assert "https://idp.example.com/sso" in result["url"]
        assert "SAMLRequest=" in result["url"]

    def test_create_authn_request_http_post(self):
        """Test creating authn request with HTTP-POST binding"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        idp = IdentityProvider(
            entity_id="https://idp.example.com",
            sso_url="https://idp.example.com/sso",
            slo_url="https://idp.example.com/slo",
            certificate="CERT",
            binding=SAMLBinding.HTTP_POST,
        )
        sp.register_idp(idp)

        result = sp.create_authn_request("https://idp.example.com")

        assert result["type"] == "post"
        assert result["url"] == "https://idp.example.com/sso"
        assert "saml_request" in result
        assert "request_id" in result
        assert result["relay_state"] == ""

    def test_create_authn_request_with_relay_state(self):
        """Test creating authn request with relay state"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        idp = IdentityProvider(
            entity_id="https://idp.example.com",
            sso_url="https://idp.example.com/sso",
            slo_url="https://idp.example.com/slo",
            certificate="CERT",
            binding=SAMLBinding.HTTP_REDIRECT,
        )
        sp.register_idp(idp)

        result = sp.create_authn_request("https://idp.example.com", relay_state="/dashboard")

        assert "RelayState=%2Fdashboard" in result["url"]

    def test_create_authn_request_nonexistent_idp(self):
        """Test creating authn request for non-existent IDP raises error"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        with pytest.raises(ValueError, match="Identity Provider not found"):
            sp.create_authn_request("https://nonexistent.example.com")

    def test_create_authn_request_contains_sp_info(self):
        """Test authn request contains SP information"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        idp = IdentityProvider(
            entity_id="https://idp.example.com",
            sso_url="https://idp.example.com/sso",
            slo_url="https://idp.example.com/slo",
            certificate="CERT",
            binding=SAMLBinding.HTTP_POST,
        )
        sp.register_idp(idp)

        result = sp.create_authn_request("https://idp.example.com")
        decoded = base64.b64decode(result["saml_request"]).decode("utf-8")

        assert "https://sp.example.com" in decoded
        assert "https://sp.example.com/acs" in decoded


class TestParseResponse:
    """Test parse_response method"""

    def test_parse_valid_response(self):
        """Test parsing valid SAML response"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        not_on_or_after = (datetime.utcnow() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Create minimal valid SAML response
        saml_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
    <saml:Issuer>https://idp.example.com</saml:Issuer>
    <saml:Assertion>
        <saml:Subject>
            <saml:NameID>user@example.com</saml:NameID>
        </saml:Subject>
        <saml:Conditions NotOnOrAfter="{not_on_or_after}">
            <saml:Audience>https://sp.example.com</saml:Audience>
        </saml:Conditions>
        <saml:AuthnStatement SessionIndex="session123"/>
        <saml:AttributeStatement>
            <saml:Attribute Name="email">
                <saml:AttributeValue>user@example.com</saml:AttributeValue>
            </saml:Attribute>
        </saml:AttributeStatement>
    </saml:Assertion>
</samlp:Response>"""

        encoded = base64.b64encode(saml_xml.encode("utf-8")).decode("utf-8")
        response = sp.parse_response(encoded)

        assert response.name_id == "user@example.com"
        assert response.session_index == "session123"
        assert response.attributes["email"] == "user@example.com"
        assert response.issuer == "https://idp.example.com"
        assert response.audience == "https://sp.example.com"

    def test_parse_response_with_multiple_attributes(self):
        """Test parsing SAML response with multiple attributes"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        not_on_or_after = (datetime.utcnow() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

        saml_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
    <saml:Issuer>https://idp.example.com</saml:Issuer>
    <saml:Assertion>
        <saml:Subject>
            <saml:NameID>user@example.com</saml:NameID>
        </saml:Subject>
        <saml:Conditions NotOnOrAfter="{not_on_or_after}">
            <saml:Audience>https://sp.example.com</saml:Audience>
        </saml:Conditions>
        <saml:AuthnStatement SessionIndex="session123"/>
        <saml:AttributeStatement>
            <saml:Attribute Name="email">
                <saml:AttributeValue>user@example.com</saml:AttributeValue>
            </saml:Attribute>
            <saml:Attribute Name="firstName">
                <saml:AttributeValue>John</saml:AttributeValue>
            </saml:Attribute>
            <saml:Attribute Name="groups">
                <saml:AttributeValue>admin</saml:AttributeValue>
                <saml:AttributeValue>users</saml:AttributeValue>
            </saml:Attribute>
        </saml:AttributeStatement>
    </saml:Assertion>
</samlp:Response>"""

        encoded = base64.b64encode(saml_xml.encode("utf-8")).decode("utf-8")
        response = sp.parse_response(encoded)

        assert response.attributes["email"] == "user@example.com"
        assert response.attributes["firstName"] == "John"
        assert response.attributes["groups"] == ["admin", "users"]

    def test_parse_response_invalid_audience(self):
        """Test parsing response with invalid audience raises error"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        not_on_or_after = (datetime.utcnow() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

        saml_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
    <saml:Issuer>https://idp.example.com</saml:Issuer>
    <saml:Assertion>
        <saml:Subject>
            <saml:NameID>user@example.com</saml:NameID>
        </saml:Subject>
        <saml:Conditions NotOnOrAfter="{not_on_or_after}">
            <saml:Audience>https://wrong-sp.example.com</saml:Audience>
        </saml:Conditions>
        <saml:AuthnStatement SessionIndex="session123"/>
    </saml:Assertion>
</samlp:Response>"""

        encoded = base64.b64encode(saml_xml.encode("utf-8")).decode("utf-8")

        with pytest.raises(ValueError, match="Invalid audience"):
            sp.parse_response(encoded)

    def test_parse_response_expired(self):
        """Test parsing expired response raises error"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        # Create expired timestamp
        not_on_or_after = (datetime.utcnow() - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

        saml_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
    <saml:Issuer>https://idp.example.com</saml:Issuer>
    <saml:Assertion>
        <saml:Subject>
            <saml:NameID>user@example.com</saml:NameID>
        </saml:Subject>
        <saml:Conditions NotOnOrAfter="{not_on_or_after}">
            <saml:Audience>https://sp.example.com</saml:Audience>
        </saml:Conditions>
        <saml:AuthnStatement SessionIndex="session123"/>
    </saml:Assertion>
</samlp:Response>"""

        encoded = base64.b64encode(saml_xml.encode("utf-8")).decode("utf-8")

        with pytest.raises(ValueError, match="SAML Response has expired"):
            sp.parse_response(encoded)

    def test_parse_response_no_assertion(self):
        """Test parsing response without assertion raises error"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        saml_xml = """<?xml version="1.0" encoding="UTF-8"?>
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
    <saml:Issuer>https://idp.example.com</saml:Issuer>
</samlp:Response>"""

        encoded = base64.b64encode(saml_xml.encode("utf-8")).decode("utf-8")

        with pytest.raises(ValueError, match="No Assertion found"):
            sp.parse_response(encoded)

    def test_parse_response_invalid_base64(self):
        """Test parsing invalid base64 raises error"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        with pytest.raises(Exception):  # base64 decode error
            sp.parse_response("invalid-base64!!!")

    def test_parse_response_invalid_xml(self):
        """Test parsing invalid XML raises error"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        invalid_xml = "<invalid>xml"
        encoded = base64.b64encode(invalid_xml.encode("utf-8")).decode("utf-8")

        with pytest.raises(ValueError, match="Failed to parse SAML Response"):
            sp.parse_response(encoded)

    def test_parse_response_empty_attributes(self):
        """Test parsing response with no attributes"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        not_on_or_after = (datetime.utcnow() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

        saml_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
    <saml:Issuer>https://idp.example.com</saml:Issuer>
    <saml:Assertion>
        <saml:Subject>
            <saml:NameID>user@example.com</saml:NameID>
        </saml:Subject>
        <saml:Conditions NotOnOrAfter="{not_on_or_after}">
            <saml:Audience>https://sp.example.com</saml:Audience>
        </saml:Conditions>
        <saml:AuthnStatement SessionIndex="session123"/>
    </saml:Assertion>
</samlp:Response>"""

        encoded = base64.b64encode(saml_xml.encode("utf-8")).decode("utf-8")
        response = sp.parse_response(encoded)

        assert response.attributes == {}


class TestCreateLogoutRequest:
    """Test create_logout_request method"""

    def test_create_logout_request(self):
        """Test creating logout request"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        idp = IdentityProvider(
            entity_id="https://idp.example.com",
            sso_url="https://idp.example.com/sso",
            slo_url="https://idp.example.com/slo",
            certificate="CERT",
        )
        sp.register_idp(idp)

        result = sp.create_logout_request("https://idp.example.com", "user@example.com", "session123")

        assert result["type"] == "redirect"
        assert "url" in result
        assert "request_id" in result
        assert "https://idp.example.com/slo" in result["url"]
        assert "SAMLRequest=" in result["url"]

    def test_create_logout_request_contains_name_id(self):
        """Test logout request contains name ID and session index"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        idp = IdentityProvider(
            entity_id="https://idp.example.com",
            sso_url="https://idp.example.com/sso",
            slo_url="https://idp.example.com/slo",
            certificate="CERT",
        )
        sp.register_idp(idp)

        result = sp.create_logout_request("https://idp.example.com", "user@example.com", "session123")

        # Decode the SAMLRequest
        from urllib.parse import parse_qs, urlparse

        parsed = urlparse(result["url"])
        params = parse_qs(parsed.query)
        saml_request = params["SAMLRequest"][0]

        # Decompress and decode
        decoded = base64.b64decode(saml_request)
        decompressed = zlib.decompress(decoded, -zlib.MAX_WBITS)
        xml_str = decompressed.decode("utf-8")

        assert "user@example.com" in xml_str
        assert "session123" in xml_str

    def test_create_logout_request_nonexistent_idp(self):
        """Test creating logout request for non-existent IDP raises error"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        with pytest.raises(ValueError, match="Identity Provider not found"):
            sp.create_logout_request("https://nonexistent.example.com", "user@example.com", "session123")

    def test_create_logout_request_format(self):
        """Test logout request has correct format"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        idp = IdentityProvider(
            entity_id="https://idp.example.com",
            sso_url="https://idp.example.com/sso",
            slo_url="https://idp.example.com/slo",
            certificate="CERT",
        )
        sp.register_idp(idp)

        result = sp.create_logout_request("https://idp.example.com", "user@example.com", "session123")

        assert result["type"] == "redirect"
        assert result["request_id"].startswith("_")


class TestGetMetadata:
    """Test get_metadata method"""

    def test_get_metadata_returns_xml(self):
        """Test get_metadata returns valid XML"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        metadata = sp.get_metadata()

        # Should parse as valid XML
        ET.fromstring(metadata)

    def test_get_metadata_contains_sp_info(self):
        """Test metadata contains SP information"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        metadata = sp.get_metadata()

        assert "https://sp.example.com" in metadata
        assert "https://sp.example.com/acs" in metadata
        assert "https://sp.example.com/slo" in metadata

    def test_get_metadata_includes_name_id_format(self):
        """Test metadata includes name ID format"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
            name_id_format=SAMLNameIDFormat.EMAIL,
        )
        sp = SAMLServiceProvider(config)

        metadata = sp.get_metadata()

        assert SAMLNameIDFormat.EMAIL.value in metadata

    def test_get_metadata_signing_requirements(self):
        """Test metadata reflects signing requirements"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
            want_assertions_signed=True,
        )
        sp = SAMLServiceProvider(config)

        metadata = sp.get_metadata()

        assert 'WantAssertionsSigned="true"' in metadata


class TestMapAttributesToUser:
    """Test map_attributes_to_user method"""

    def test_map_basic_attributes(self):
        """Test mapping basic SAML attributes"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        attributes = {"email": "user@example.com", "givenName": "John", "sn": "Doe"}

        user_data = sp.map_attributes_to_user(attributes)

        assert user_data["email"] == "user@example.com"
        assert user_data["first_name"] == "John"
        assert user_data["last_name"] == "Doe"

    def test_map_ws_federation_attributes(self):
        """Test mapping WS-Federation style attributes"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        attributes = {
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress": "user@example.com",
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname": "John",
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname": "Doe",
        }

        user_data = sp.map_attributes_to_user(attributes)

        assert user_data["email"] == "user@example.com"
        assert user_data["first_name"] == "John"
        assert user_data["last_name"] == "Doe"

    def test_map_groups_and_roles(self):
        """Test mapping groups and roles"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        attributes = {"groups": ["admin", "users"], "role": "administrator"}

        user_data = sp.map_attributes_to_user(attributes)

        assert user_data["groups"] == ["admin", "users"]
        assert user_data["role"] == "administrator"

    def test_map_empty_attributes(self):
        """Test mapping empty attributes"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        user_data = sp.map_attributes_to_user({})

        assert user_data == {}

    def test_map_unmapped_attributes(self):
        """Test unmapped attributes are ignored"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        attributes = {"email": "user@example.com", "custom_attribute": "value", "unknown": "data"}

        user_data = sp.map_attributes_to_user(attributes)

        assert user_data["email"] == "user@example.com"
        assert "custom_attribute" not in user_data
        assert "unknown" not in user_data

    def test_map_display_name(self):
        """Test mapping display name"""
        config = SAMLConfig(
            entity_id="https://sp.example.com",
            acs_url="https://sp.example.com/acs",
            slo_url="https://sp.example.com/slo",
        )
        sp = SAMLServiceProvider(config)

        attributes = {"displayName": "John Doe", "uid": "johndoe"}

        user_data = sp.map_attributes_to_user(attributes)

        assert user_data["full_name"] == "John Doe"
        assert user_data["username"] == "johndoe"


class TestGlobalFunctions:
    """Test global SAML functions"""

    def test_get_saml_sp_creates_instance(self):
        """Test get_saml_sp creates global instance"""
        # Reset global instance
        import src.core.sso.saml as saml_module

        saml_module._saml_sp = None

        sp = get_saml_sp()

        assert sp is not None
        assert isinstance(sp, SAMLServiceProvider)

    def test_get_saml_sp_returns_same_instance(self):
        """Test get_saml_sp returns same instance"""
        sp1 = get_saml_sp()
        sp2 = get_saml_sp()

        assert sp1 is sp2

    def test_configure_saml_sp(self):
        """Test configure_saml_sp sets new instance"""
        config = SAMLConfig(
            entity_id="https://custom.example.com",
            acs_url="https://custom.example.com/acs",
            slo_url="https://custom.example.com/slo",
        )

        configure_saml_sp(config)
        sp = get_saml_sp()

        assert sp.config.entity_id == "https://custom.example.com"
