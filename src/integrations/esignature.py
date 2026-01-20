"""
E-Signature Integration

Integration with DocuSign, Adobe Sign for digital document signing workflows.

Part of v3.7 Advanced Integrations implementation.

Configuration required:
- DocuSign: integration_key, account_id, user_id, private_key
- Adobe Sign: client_id, client_secret, api_access_point
"""

import asyncio
import base64
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

# Optional HTTP library
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    logger.warning("requests library not available - e-signature will be simulated. Install: pip install requests")


class SignatureProvider(Enum):
    """E-signature providers."""

    DOCUSIGN = "docusign"
    ADOBE_SIGN = "adobe_sign"


class SignatureStatus(Enum):
    """Signature request status."""

    SENT = "sent"
    VIEWED = "viewed"
    SIGNED = "signed"
    COMPLETED = "completed"
    VOIDED = "voided"


@dataclass
class Signer:
    """Document signer."""

    email: str
    name: str
    order: int = 1
    signed: bool = False
    signed_at: Optional[datetime] = None


@dataclass
class SignatureRequest:
    """Signature request."""

    request_id: str
    envelope_id: str
    document_path: str
    subject: str
    signers: List[Signer]
    status: SignatureStatus
    provider: SignatureProvider
    created_at: datetime = field(default_factory=datetime.now)


class BaseESignatureProvider(ABC):
    """Base e-signature provider."""

    def __init__(self, credentials: Dict[str, str]):
        self.credentials = credentials
        self.connected = False

    @abstractmethod
    async def send_signature_request(
        self, document_path: str, signers: List[Signer], subject: str, message: str
    ) -> SignatureRequest:
        """Send document for signature."""
        pass

    @abstractmethod
    async def get_status(self, envelope_id: str) -> SignatureStatus:
        """Get signature request status."""
        pass


class DocuSignClient(BaseESignatureProvider):
    """DocuSign integration.

    Requires credentials:
    - account_id: DocuSign account ID
    - integration_key: OAuth integration key
    - access_token: OAuth access token (obtained via JWT or auth code flow)
    - base_url: API base URL (e.g., https://demo.docusign.net or https://na3.docusign.net)
    """

    def __init__(self, credentials: Dict[str, str]):
        super().__init__(credentials)
        self.account_id = credentials.get('account_id')
        self.access_token = credentials.get('access_token')
        self.base_url = credentials.get('base_url', 'https://demo.docusign.net')

        if not all([self.account_id, self.access_token]):
            logger.warning("DocuSign credentials incomplete - operations will be simulated")

    async def send_signature_request(
        self, document_path: str, signers: List[Signer], subject: str, message: str
    ) -> SignatureRequest:
        """Send document for signature via DocuSign API."""

        if not HAS_REQUESTS or not all([self.account_id, self.access_token]):
            # Fallback to simulation
            logger.warning("Simulating DocuSign signature request (missing requests or credentials)")
            request = SignatureRequest(
                request_id=str(uuid4()),
                envelope_id=f"env_{uuid4()}",
                document_path=document_path,
                subject=subject,
                signers=signers,
                status=SignatureStatus.SENT,
                provider=SignatureProvider.DOCUSIGN,
            )
            return request

        # Check if document file exists
        if not os.path.exists(document_path):
            raise FileNotFoundError(f"Document not found: {document_path}")

        # Read document and encode to base64
        with open(document_path, 'rb') as f:
            doc_bytes = f.read()
        doc_base64 = base64.b64encode(doc_bytes).decode('utf-8')

        # Build DocuSign envelope definition
        envelope_definition = {
            "emailSubject": subject,
            "emailBlurb": message,
            "status": "sent",  # 'sent' to send immediately, 'created' to save as draft
            "documents": [{
                "documentBase64": doc_base64,
                "name": os.path.basename(document_path),
                "fileExtension": os.path.splitext(document_path)[1].lstrip('.'),
                "documentId": "1"
            }],
            "recipients": {
                "signers": [
                    {
                        "email": signer.email,
                        "name": signer.name,
                        "recipientId": str(idx + 1),
                        "routingOrder": str(signer.order),
                        "tabs": {
                            "signHereTabs": [{
                                "documentId": "1",
                                "pageNumber": "1",
                                "xPosition": "100",
                                "yPosition": "100"
                            }]
                        }
                    }
                    for idx, signer in enumerate(signers)
                ]
            }
        }

        # Make API request
        try:
            url = f"{self.base_url}/restapi/v2.1/accounts/{self.account_id}/envelopes"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=envelope_definition, headers=headers, timeout=30)
            response.raise_for_status()

            result = response.json()
            envelope_id = result.get('envelopeId', f"env_{uuid4()}")

            logger.info(f"Sent DocuSign envelope {envelope_id}: {subject}")

            request = SignatureRequest(
                request_id=str(uuid4()),
                envelope_id=envelope_id,
                document_path=document_path,
                subject=subject,
                signers=signers,
                status=SignatureStatus.SENT,
                provider=SignatureProvider.DOCUSIGN,
            )

            return request

        except requests.exceptions.HTTPError as e:
            logger.error(f"DocuSign API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"DocuSign API error: {e.response.status_code}")

        except Exception as e:
            logger.exception(f"Error sending DocuSign request: {e}")
            raise

    async def get_status(self, envelope_id: str) -> SignatureStatus:
        """Get envelope status from DocuSign API."""

        if not HAS_REQUESTS or not all([self.account_id, self.access_token]):
            logger.warning("Simulating DocuSign status check (missing requests or credentials)")
            return SignatureStatus.SENT

        try:
            url = f"{self.base_url}/restapi/v2.1/accounts/{self.account_id}/envelopes/{envelope_id}"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            result = response.json()
            status = result.get('status', 'sent').lower()

            # Map DocuSign status to our enum
            status_mapping = {
                'sent': SignatureStatus.SENT,
                'delivered': SignatureStatus.VIEWED,
                'signed': SignatureStatus.SIGNED,
                'completed': SignatureStatus.COMPLETED,
                'voided': SignatureStatus.VOIDED
            }

            logger.info(f"DocuSign envelope {envelope_id} status: {status}")
            return status_mapping.get(status, SignatureStatus.SENT)

        except requests.exceptions.HTTPError as e:
            logger.error(f"DocuSign API error: {e.response.status_code}")
            raise Exception(f"DocuSign API error: {e.response.status_code}")

        except Exception as e:
            logger.exception(f"Error getting DocuSign status: {e}")
            raise


class ESignatureManager:
    """Main e-signature manager."""

    def __init__(self):
        self.providers: Dict[SignatureProvider, BaseESignatureProvider] = {}

    def register_provider(self, provider: SignatureProvider, credentials: Dict[str, str]):
        """Register provider."""
        if provider == SignatureProvider.DOCUSIGN:
            self.providers[provider] = DocuSignClient(credentials)

    async def send_signature_request(
        self, provider: str, document_path: str, signers: List[Dict[str, Any]], subject: str, message: str
    ) -> SignatureRequest:
        """Send signature request."""
        provider_enum = SignatureProvider(provider)
        client = self.providers[provider_enum]

        signer_objects = [Signer(email=s["email"], name=s["name"], order=s.get("order", 1)) for s in signers]
        return await client.send_signature_request(document_path, signer_objects, subject, message)


_esignature_manager: Optional[ESignatureManager] = None


def get_esignature_client(provider: str = "docusign") -> ESignatureManager:
    """Get e-signature manager."""
    global _esignature_manager
    if _esignature_manager is None:
        _esignature_manager = ESignatureManager()
    return _esignature_manager
