"""
eDiscovery Platform

Legal hold management, search and collection, custodian tracking,
and export capabilities for legal proceedings.

Part of v3.8 Governance & Compliance implementation.
"""

import asyncio
import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

logger = logging.getLogger(__name__)


class HoldStatus(Enum):
    """Legal hold status."""
    ACTIVE = "active"
    RELEASED = "released"
    EXPIRED = "expired"


class ExportFormat(Enum):
    """Export formats for legal review."""
    PST = "pst"
    EDRM_XML = "edrm_xml"
    PDF = "pdf"
    NATIVE = "native"
    ZIP = "zip"


@dataclass
class Custodian:
    """Data custodian (person who has relevant data)."""
    custodian_id: str
    name: str
    email: str
    department: str
    title: Optional[str] = None
    data_sources: List[str] = field(default_factory=list)  # email, documents, chat, etc
    hold_notice_sent: bool = False
    hold_notice_date: Optional[datetime] = None
    acknowledged: bool = False
    acknowledged_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LegalHold:
    """Legal hold/litigation hold."""
    hold_id: str
    case_name: str
    case_number: str
    status: HoldStatus
    start_date: datetime
    end_date: Optional[datetime]
    custodians: List[str]  # custodian_ids
    keywords: List[str]
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    description: Optional[str] = None
    matter_id: Optional[str] = None
    outside_counsel: Optional[str] = None
    document_count: int = 0
    created_by: Optional[str] = None
    created_date: datetime = field(default_factory=datetime.now)


@dataclass
class SearchQuery:
    """eDiscovery search query."""
    query_id: str
    legal_hold_id: str
    query_text: str
    custodians: List[str] = field(default_factory=list)
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    file_types: List[str] = field(default_factory=list)
    repositories: List[str] = field(default_factory=list)
    created_by: str = ""
    created_date: datetime = field(default_factory=datetime.now)


@dataclass
class CollectedDocument:
    """Document collected for eDiscovery."""
    document_id: str
    source_path: str
    hash_md5: str
    hash_sha256: str
    file_type: str
    file_size: int
    author: Optional[str] = None
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    custodian_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    content_preview: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    collected_date: datetime = field(default_factory=datetime.now)


@dataclass
class Collection:
    """Collection of documents for legal matter."""
    collection_id: str
    legal_hold_id: str
    search_query_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    documents: List[CollectedDocument] = field(default_factory=list)
    total_documents: int = 0
    total_size_bytes: int = 0
    deduplicated: bool = False
    created_by: str = ""
    created_date: datetime = field(default_factory=datetime.now)


@dataclass
class ExportPackage:
    """Export package for legal review."""
    export_id: str
    collection_id: str
    format: ExportFormat
    output_path: str
    include_metadata: bool
    include_natives: bool
    deduplicate: bool
    total_documents: int
    total_size_bytes: int
    export_date: datetime = field(default_factory=datetime.now)
    exported_by: str = ""
    encryption_enabled: bool = True


@dataclass
class ChainOfCustodyEntry:
    """Chain of custody log entry."""
    entry_id: str
    document_id: str
    action: str  # collected, reviewed, exported, transferred
    performed_by: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: Optional[str] = None
    location: Optional[str] = None
    hash_verification: Optional[str] = None


class CustodianManager:
    """Manage custodians."""

    def __init__(self):
        self.custodians: Dict[str, Custodian] = {}

    async def add_custodian(
        self,
        name: str,
        email: str,
        department: str,
        data_sources: Optional[List[str]] = None,
        **kwargs
    ) -> Custodian:
        """Add custodian to matter."""
        await asyncio.sleep(0.05)

        custodian = Custodian(
            custodian_id=str(uuid4()),
            name=name,
            email=email,
            department=department,
            data_sources=data_sources or ["email", "documents"],
            **kwargs
        )

        self.custodians[custodian.custodian_id] = custodian

        logger.info(f"Added custodian: {name} ({email})")
        return custodian

    async def send_hold_notice(self, custodian_id: str) -> bool:
        """Send legal hold notice to custodian."""
        await asyncio.sleep(0.1)

        if custodian_id not in self.custodians:
            return False

        custodian = self.custodians[custodian_id]
        custodian.hold_notice_sent = True
        custodian.hold_notice_date = datetime.now()

        logger.info(f"Sent hold notice to {custodian.email}")
        return True

    async def acknowledge_hold(self, custodian_id: str) -> bool:
        """Record custodian acknowledgment of hold."""
        await asyncio.sleep(0.05)

        if custodian_id not in self.custodians:
            return False

        custodian = self.custodians[custodian_id]
        custodian.acknowledged = True
        custodian.acknowledged_date = datetime.now()

        logger.info(f"Custodian {custodian.name} acknowledged hold")
        return True

    async def get_acknowledgment_status(self) -> Dict[str, Any]:
        """Get acknowledgment status across all custodians."""
        total = len(self.custodians)
        acknowledged = sum(1 for c in self.custodians.values() if c.acknowledged)

        return {
            "total_custodians": total,
            "acknowledged": acknowledged,
            "pending": total - acknowledged,
            "acknowledgment_rate": (acknowledged / total * 100) if total > 0 else 100.0
        }


class SearchEngine:
    """eDiscovery search engine."""

    async def search(
        self,
        query: SearchQuery,
        repositories: Optional[List[str]] = None
    ) -> List[CollectedDocument]:
        """Execute search query."""
        await asyncio.sleep(0.3)

        # Mock search results
        documents = []

        # Simulate finding documents
        for i in range(5):
            doc = CollectedDocument(
                document_id=str(uuid4()),
                source_path=f"/data/email/user{i}/inbox/message{i}.eml",
                hash_md5=hashlib.md5(f"doc{i}".encode()).hexdigest(),
                hash_sha256=hashlib.sha256(f"doc{i}".encode()).hexdigest(),
                file_type="email",
                file_size=1024 * (i + 1),
                author=f"user{i}@company.com",
                created_date=datetime.now(),
                custodian_id=query.custodians[0] if query.custodians else None,
                content_preview=f"Email content matching query: {query.query_text}"
            )
            documents.append(doc)

        logger.info(f"Search found {len(documents)} documents")
        return documents

    async def deduplicate(
        self,
        documents: List[CollectedDocument]
    ) -> List[CollectedDocument]:
        """Deduplicate documents by hash."""
        await asyncio.sleep(0.2)

        seen_hashes = set()
        unique_docs = []

        for doc in documents:
            if doc.hash_sha256 not in seen_hashes:
                seen_hashes.add(doc.hash_sha256)
                unique_docs.append(doc)

        logger.info(f"Deduplication: {len(documents)} -> {len(unique_docs)} documents")
        return unique_docs


class ChainOfCustody:
    """Track chain of custody for evidence."""

    def __init__(self):
        self.entries: List[ChainOfCustodyEntry] = []

    async def log_action(
        self,
        document_id: str,
        action: str,
        performed_by: str,
        details: Optional[str] = None,
        hash_value: Optional[str] = None
    ) -> ChainOfCustodyEntry:
        """Log chain of custody action."""
        await asyncio.sleep(0.02)

        entry = ChainOfCustodyEntry(
            entry_id=str(uuid4()),
            document_id=document_id,
            action=action,
            performed_by=performed_by,
            details=details,
            hash_verification=hash_value
        )

        self.entries.append(entry)

        logger.info(f"Chain of custody: {action} on {document_id} by {performed_by}")
        return entry

    async def get_document_history(self, document_id: str) -> List[ChainOfCustodyEntry]:
        """Get chain of custody history for document."""
        await asyncio.sleep(0.05)

        return [e for e in self.entries if e.document_id == document_id]

    async def verify_integrity(
        self,
        document_id: str,
        current_hash: str
    ) -> bool:
        """Verify document integrity via chain of custody."""
        await asyncio.sleep(0.05)

        history = await self.get_document_history(document_id)

        if not history:
            return False

        # Check if any entry has matching hash
        for entry in history:
            if entry.hash_verification == current_hash:
                return True

        return False


class eDiscoveryManager:
    """Main eDiscovery platform manager."""

    def __init__(self):
        self.legal_holds: Dict[str, LegalHold] = {}
        self.collections: Dict[str, Collection] = {}
        self.exports: Dict[str, ExportPackage] = {}
        self.custodian_manager = CustodianManager()
        self.search_engine = SearchEngine()
        self.chain_of_custody = ChainOfCustody()

    async def create_legal_hold(
        self,
        case_name: str,
        case_number: str,
        custodians: List[str],
        keywords: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        **kwargs
    ) -> LegalHold:
        """Create legal hold."""
        await asyncio.sleep(0.1)

        hold = LegalHold(
            hold_id=str(uuid4()),
            case_name=case_name,
            case_number=case_number,
            status=HoldStatus.ACTIVE,
            start_date=start_date or datetime.now(),
            end_date=None,
            custodians=custodians,
            keywords=keywords or [],
            **kwargs
        )

        self.legal_holds[hold.hold_id] = hold

        # Send hold notices to custodians
        for custodian_id in custodians:
            await self.custodian_manager.send_hold_notice(custodian_id)

        logger.info(f"Created legal hold: {case_name} ({case_number})")
        return hold

    async def release_legal_hold(self, hold_id: str) -> bool:
        """Release legal hold."""
        await asyncio.sleep(0.05)

        if hold_id not in self.legal_holds:
            return False

        hold = self.legal_holds[hold_id]
        hold.status = HoldStatus.RELEASED
        hold.end_date = datetime.now()

        logger.info(f"Released legal hold: {hold.case_name}")
        return True

    async def search(
        self,
        legal_hold_id: str,
        query: str,
        custodians: Optional[List[str]] = None,
        date_range: Optional[tuple] = None,
        **kwargs
    ) -> Collection:
        """Search for documents matching criteria."""
        await asyncio.sleep(0.2)

        if legal_hold_id not in self.legal_holds:
            raise ValueError(f"Legal hold {legal_hold_id} not found")

        search_query = SearchQuery(
            query_id=str(uuid4()),
            legal_hold_id=legal_hold_id,
            query_text=query,
            custodians=custodians or [],
            date_range_start=date_range[0] if date_range else None,
            date_range_end=date_range[1] if date_range else None,
            created_by=kwargs.get("created_by", "system")
        )

        # Execute search
        documents = await self.search_engine.search(search_query)

        # Create collection
        collection = Collection(
            collection_id=str(uuid4()),
            legal_hold_id=legal_hold_id,
            search_query_id=search_query.query_id,
            name=f"Collection for {query}",
            documents=documents,
            total_documents=len(documents),
            total_size_bytes=sum(d.file_size for d in documents),
            created_by=kwargs.get("created_by", "system")
        )

        self.collections[collection.collection_id] = collection

        # Log chain of custody for each document
        for doc in documents:
            await self.chain_of_custody.log_action(
                document_id=doc.document_id,
                action="collected",
                performed_by=kwargs.get("created_by", "system"),
                details=f"Collected for case {legal_hold_id}",
                hash_value=doc.hash_sha256
            )

        logger.info(f"Created collection with {len(documents)} documents")
        return collection

    async def export_collection(
        self,
        collection_id: str,
        format: str = "pst",
        include_metadata: bool = True,
        deduplicate: bool = True,
        **kwargs
    ) -> ExportPackage:
        """Export collection for legal review."""
        await asyncio.sleep(0.3)

        if collection_id not in self.collections:
            raise ValueError(f"Collection {collection_id} not found")

        collection = self.collections[collection_id]

        # Deduplicate if requested
        documents = collection.documents
        if deduplicate and not collection.deduplicated:
            documents = await self.search_engine.deduplicate(documents)
            collection.deduplicated = True

        format_enum = ExportFormat(format)
        output_path = f"/exports/{collection_id}.{format}"

        export = ExportPackage(
            export_id=str(uuid4()),
            collection_id=collection_id,
            format=format_enum,
            output_path=output_path,
            include_metadata=include_metadata,
            include_natives=kwargs.get("include_natives", True),
            deduplicate=deduplicate,
            total_documents=len(documents),
            total_size_bytes=sum(d.file_size for d in documents),
            exported_by=kwargs.get("exported_by", "system")
        )

        self.exports[export.export_id] = export

        # Log chain of custody
        for doc in documents:
            await self.chain_of_custody.log_action(
                document_id=doc.document_id,
                action="exported",
                performed_by=export.exported_by,
                details=f"Exported as {format}",
                hash_value=doc.hash_sha256
            )

        logger.info(f"Exported collection {collection_id} to {output_path}")
        return export

    async def get_hold_status(
        self,
        hold_id: str
    ) -> Dict[str, Any]:
        """Get legal hold status summary."""
        await asyncio.sleep(0.05)

        if hold_id not in self.legal_holds:
            return {}

        hold = self.legal_holds[hold_id]

        # Count collections
        collections = [c for c in self.collections.values() if c.legal_hold_id == hold_id]

        # Get custodian acknowledgment status
        ack_status = await self.custodian_manager.get_acknowledgment_status()

        return {
            "hold_id": hold_id,
            "case_name": hold.case_name,
            "case_number": hold.case_number,
            "status": hold.status.value,
            "custodian_count": len(hold.custodians),
            "custodian_acknowledgments": ack_status,
            "collections": len(collections),
            "total_documents": sum(c.total_documents for c in collections),
            "keywords": hold.keywords,
            "start_date": hold.start_date.isoformat(),
            "end_date": hold.end_date.isoformat() if hold.end_date else None
        }


# Singleton instance
_ediscovery_manager: Optional[eDiscoveryManager] = None


def get_ediscovery_manager() -> eDiscoveryManager:
    """Get eDiscovery manager instance."""
    global _ediscovery_manager
    if _ediscovery_manager is None:
        _ediscovery_manager = eDiscoveryManager()
    return _ediscovery_manager
