"""
ERP Integration Framework

Provides integrations with major ERP systems:
- SAP (S/4HANA, ECC)
- Oracle ERP Cloud / NetSuite
- Microsoft Dynamics 365
- Generic REST/SOAP API support
- Data synchronization
- Real-time updates
"""

from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import uuid
import hashlib


class ERPSystem(str, Enum):
    """Supported ERP systems"""
    SAP_S4HANA = "sap_s4hana"
    SAP_ECC = "sap_ecc"
    ORACLE_ERP_CLOUD = "oracle_erp_cloud"
    ORACLE_NETSUITE = "oracle_netsuite"
    MICROSOFT_DYNAMICS_365 = "microsoft_dynamics_365"
    MICROSOFT_DYNAMICS_AX = "microsoft_dynamics_ax"
    SAGE_INTACCT = "sage_intacct"
    EPICOR = "epicor"
    INFOR = "infor"
    GENERIC_REST = "generic_rest"
    GENERIC_SOAP = "generic_soap"


class SyncDirection(str, Enum):
    """Data synchronization direction"""
    BIDIRECTIONAL = "bidirectional"
    TO_ERP = "to_erp"
    FROM_ERP = "from_erp"


class SyncStatus(str, Enum):
    """Synchronization status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class EntityType(str, Enum):
    """ERP entity types"""
    CUSTOMER = "customer"
    VENDOR = "vendor"
    PRODUCT = "product"
    INVOICE = "invoice"
    PURCHASE_ORDER = "purchase_order"
    SALES_ORDER = "sales_order"
    PAYMENT = "payment"
    JOURNAL_ENTRY = "journal_entry"
    ACCOUNT = "account"
    EMPLOYEE = "employee"


@dataclass
class ERPConnection:
    """ERP system connection configuration"""
    id: str
    name: str
    system_type: ERPSystem
    base_url: str
    auth_type: str  # oauth2, api_key, basic, saml
    credentials: Dict[str, str]  # Encrypted in production
    tenant_id: Optional[str] = None
    company_code: Optional[str] = None
    environment: str = "production"  # production, sandbox, test
    timeout: int = 30
    retry_count: int = 3
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_sync: Optional[datetime] = None


@dataclass
class FieldMapping:
    """Field mapping between DMS and ERP"""
    source_field: str
    target_field: str
    transformation: Optional[str] = None  # Python expression or function name
    required: bool = False
    default_value: Optional[Any] = None


@dataclass
class EntityMapping:
    """Entity mapping configuration"""
    id: str
    connection_id: str
    entity_type: EntityType
    dms_table: str
    erp_endpoint: str
    field_mappings: List[FieldMapping] = field(default_factory=list)
    sync_direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    auto_sync: bool = False
    sync_interval_minutes: int = 60
    filter_conditions: Optional[str] = None


@dataclass
class SyncLog:
    """Synchronization log entry"""
    id: str
    connection_id: str
    entity_type: EntityType
    direction: str
    status: SyncStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    records_processed: int = 0
    records_success: int = 0
    records_failed: int = 0
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


class SAPConnector:
    """SAP S/4HANA and ECC connector"""

    def __init__(self, connection: ERPConnection):
        self.connection = connection
        self.session = None

    def connect(self) -> bool:
        """Establish connection to SAP"""
        try:
            # In production, use SAP PyRFC or OData API
            # from pyrfc import Connection
            # self.session = Connection(
            #     user=self.connection.credentials['username'],
            #     passwd=self.connection.credentials['password'],
            #     ashost=self.connection.base_url,
            #     sysnr=self.connection.credentials.get('system_number'),
            #     client=self.connection.credentials.get('client')
            # )

            print(f"[SAP] Connected to {self.connection.base_url}")
            return True

        except Exception as e:
            print(f"[SAP] Connection failed: {e}")
            return False

    def read_data(
        self,
        entity_type: EntityType,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Read data from SAP"""
        # Simulated data retrieval
        # In production, use BAPI calls or OData queries

        if entity_type == EntityType.CUSTOMER:
            # Example: BAPI_CUSTOMER_GETLIST
            return [
                {
                    'KUNNR': '0000100001',  # Customer number
                    'NAME1': 'Sample Customer GmbH',
                    'STRAS': 'Main Street 123',
                    'ORT01': 'Munich',
                    'LAND1': 'DE'
                }
            ]

        elif entity_type == EntityType.INVOICE:
            # Example: BAPI_ACC_INVOICE_RECEIPT_GET
            return [
                {
                    'BELNR': '1900000001',  # Document number
                    'BUKRS': '1000',  # Company code
                    'GJAHR': '2024',  # Fiscal year
                    'WRBTR': 1500.00,  # Amount
                    'WAERS': 'EUR'  # Currency
                }
            ]

        return []

    def write_data(
        self,
        entity_type: EntityType,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Write data to SAP"""
        # In production, use BAPI calls
        # Example: BAPI_CUSTOMER_CREATEFROMDATA1

        if entity_type == EntityType.CUSTOMER:
            # Simulate customer creation
            customer_number = f"000{uuid.uuid4().hex[:7].upper()}"
            return {
                'success': True,
                'KUNNR': customer_number,
                'message': 'Customer created successfully'
            }

        return {'success': False, 'error': 'Unsupported entity type'}

    def disconnect(self):
        """Close SAP connection"""
        if self.session:
            # self.session.close()
            print("[SAP] Disconnected")


class OracleERPConnector:
    """Oracle ERP Cloud / NetSuite connector"""

    def __init__(self, connection: ERPConnection):
        self.connection = connection
        self.access_token = None

    def connect(self) -> bool:
        """Establish connection to Oracle ERP"""
        try:
            # In production, use Oracle REST API with OAuth2
            # Authenticate and get access token

            print(f"[Oracle] Connected to {self.connection.base_url}")
            self.access_token = "simulated_token"
            return True

        except Exception as e:
            print(f"[Oracle] Connection failed: {e}")
            return False

    def read_data(
        self,
        entity_type: EntityType,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Read data from Oracle ERP"""
        # Use REST API endpoints

        if entity_type == EntityType.CUSTOMER:
            # GET /fscmRestApi/resources/11.13.18.05/customers
            return [
                {
                    'PartyId': 100001,
                    'PartyNumber': 'CUST-001',
                    'OrganizationName': 'Oracle Customer Ltd',
                    'Address': 'Oracle Parkway 1',
                    'City': 'Redwood City',
                    'Country': 'US'
                }
            ]

        elif entity_type == EntityType.INVOICE:
            # GET /fscmRestApi/resources/11.13.18.05/invoices
            return [
                {
                    'InvoiceId': 200001,
                    'InvoiceNumber': 'INV-2024-001',
                    'InvoiceAmount': 2500.00,
                    'InvoiceCurrency': 'USD',
                    'InvoiceDate': '2024-01-15'
                }
            ]

        return []

    def write_data(
        self,
        entity_type: EntityType,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Write data to Oracle ERP"""
        # POST to REST API endpoints

        if entity_type == EntityType.CUSTOMER:
            # POST /fscmRestApi/resources/11.13.18.05/customers
            return {
                'success': True,
                'PartyId': 100000 + hash(str(data)) % 10000,
                'PartyNumber': f"CUST-{uuid.uuid4().hex[:6].upper()}"
            }

        return {'success': False, 'error': 'Unsupported entity type'}


class Dynamics365Connector:
    """Microsoft Dynamics 365 connector"""

    def __init__(self, connection: ERPConnection):
        self.connection = connection
        self.access_token = None

    def connect(self) -> bool:
        """Establish connection to Dynamics 365"""
        try:
            # In production, use Microsoft Graph API with OAuth2
            # from msal import ConfidentialClientApplication

            print(f"[Dynamics365] Connected to {self.connection.base_url}")
            self.access_token = "simulated_token"
            return True

        except Exception as e:
            print(f"[Dynamics365] Connection failed: {e}")
            return False

    def read_data(
        self,
        entity_type: EntityType,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Read data from Dynamics 365"""
        # Use Web API (OData)

        if entity_type == EntityType.CUSTOMER:
            # GET /api/data/v9.2/accounts
            return [
                {
                    'accountid': uuid.uuid4(),
                    'accountnumber': 'ACC-001',
                    'name': 'Microsoft Customer Inc',
                    'address1_line1': 'One Microsoft Way',
                    'address1_city': 'Redmond',
                    'address1_country': 'USA'
                }
            ]

        elif entity_type == EntityType.INVOICE:
            # GET /api/data/v9.2/invoices
            return [
                {
                    'invoiceid': uuid.uuid4(),
                    'invoicenumber': 'INV-2024-001',
                    'totalamount': 3000.00,
                    'transactioncurrencyid': 'USD'
                }
            ]

        return []

    def write_data(
        self,
        entity_type: EntityType,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Write data to Dynamics 365"""
        # POST to Web API

        if entity_type == EntityType.CUSTOMER:
            # POST /api/data/v9.2/accounts
            return {
                'success': True,
                'accountid': str(uuid.uuid4()),
                'accountnumber': f"ACC-{uuid.uuid4().hex[:6].upper()}"
            }

        return {'success': False, 'error': 'Unsupported entity type'}


class ERPIntegrationEngine:
    """Main ERP integration engine"""

    def __init__(self, database=None):
        self.database = database
        self.connections: Dict[str, ERPConnection] = {}
        self.mappings: Dict[str, EntityMapping] = {}
        self.sync_logs: List[SyncLog] = []
        self.connectors: Dict[str, Any] = {}

    def register_connection(self, connection: ERPConnection) -> str:
        """Register ERP connection"""
        self.connections[connection.id] = connection
        return connection.id

    def create_mapping(self, mapping: EntityMapping) -> str:
        """Create entity mapping"""
        self.mappings[mapping.id] = mapping
        return mapping.id

    def get_connector(self, connection_id: str) -> Optional[Any]:
        """Get or create connector for connection"""
        if connection_id not in self.connections:
            return None

        if connection_id in self.connectors:
            return self.connectors[connection_id]

        connection = self.connections[connection_id]

        # Create appropriate connector
        if connection.system_type in [ERPSystem.SAP_S4HANA, ERPSystem.SAP_ECC]:
            connector = SAPConnector(connection)
        elif connection.system_type in [ERPSystem.ORACLE_ERP_CLOUD, ERPSystem.ORACLE_NETSUITE]:
            connector = OracleERPConnector(connection)
        elif connection.system_type in [ERPSystem.MICROSOFT_DYNAMICS_365, ERPSystem.MICROSOFT_DYNAMICS_AX]:
            connector = Dynamics365Connector(connection)
        else:
            return None

        # Connect
        if connector.connect():
            self.connectors[connection_id] = connector
            return connector

        return None

    def sync_entity(
        self,
        mapping_id: str,
        direction: Optional[SyncDirection] = None
    ) -> str:
        """Synchronize entity data"""
        if mapping_id not in self.mappings:
            return ""

        mapping = self.mappings[mapping_id]
        sync_direction = direction or mapping.sync_direction

        # Create sync log
        log_id = str(uuid.uuid4())
        log = SyncLog(
            id=log_id,
            connection_id=mapping.connection_id,
            entity_type=mapping.entity_type,
            direction=sync_direction.value,
            status=SyncStatus.IN_PROGRESS,
            started_at=datetime.now()
        )

        self.sync_logs.append(log)

        try:
            # Get connector
            connector = self.get_connector(mapping.connection_id)
            if not connector:
                log.status = SyncStatus.FAILED
                log.error_message = "Failed to connect to ERP system"
                log.completed_at = datetime.now()
                return log_id

            # Sync based on direction
            if sync_direction in [SyncDirection.FROM_ERP, SyncDirection.BIDIRECTIONAL]:
                self._sync_from_erp(mapping, connector, log)

            if sync_direction in [SyncDirection.TO_ERP, SyncDirection.BIDIRECTIONAL]:
                self._sync_to_erp(mapping, connector, log)

            log.status = SyncStatus.COMPLETED
            log.completed_at = datetime.now()

            # Update last sync time
            self.connections[mapping.connection_id].last_sync = datetime.now()

        except Exception as e:
            log.status = SyncStatus.FAILED
            log.error_message = str(e)
            log.completed_at = datetime.now()
            print(f"[Sync] Error: {e}")

        return log_id

    def _sync_from_erp(
        self,
        mapping: EntityMapping,
        connector: Any,
        log: SyncLog
    ):
        """Sync data from ERP to DMS"""
        # Read from ERP
        erp_data = connector.read_data(mapping.entity_type)
        log.records_processed = len(erp_data)

        # Transform and insert into DMS database
        for record in erp_data:
            try:
                # Apply field mappings
                transformed = self._apply_field_mappings(
                    record,
                    mapping.field_mappings,
                    reverse=False
                )

                # Insert into DMS database
                # self._insert_to_database(mapping.dms_table, transformed)

                log.records_success += 1

            except Exception as e:
                log.records_failed += 1
                print(f"[Sync] Failed to sync record: {e}")

    def _sync_to_erp(
        self,
        mapping: EntityMapping,
        connector: Any,
        log: SyncLog
    ):
        """Sync data from DMS to ERP"""
        # Read from DMS database
        # dms_data = self._read_from_database(mapping.dms_table)

        # Simulated data
        dms_data = []

        log.records_processed += len(dms_data)

        # Transform and write to ERP
        for record in dms_data:
            try:
                # Apply field mappings (reverse)
                transformed = self._apply_field_mappings(
                    record,
                    mapping.field_mappings,
                    reverse=True
                )

                # Write to ERP
                result = connector.write_data(mapping.entity_type, transformed)

                if result.get('success'):
                    log.records_success += 1
                else:
                    log.records_failed += 1

            except Exception as e:
                log.records_failed += 1
                print(f"[Sync] Failed to sync record: {e}")

    def _apply_field_mappings(
        self,
        data: Dict[str, Any],
        mappings: List[FieldMapping],
        reverse: bool = False
    ) -> Dict[str, Any]:
        """Apply field mappings to data"""
        result = {}

        for mapping in mappings:
            source = mapping.target_field if reverse else mapping.source_field
            target = mapping.source_field if reverse else mapping.target_field

            # Get value
            value = data.get(source, mapping.default_value)

            # Apply transformation if specified
            if mapping.transformation and value is not None:
                # In production, use safe evaluation
                # For now, just pass through
                pass

            result[target] = value

        return result

    def get_sync_status(self, log_id: str) -> Optional[SyncLog]:
        """Get synchronization status"""
        for log in self.sync_logs:
            if log.id == log_id:
                return log
        return None

    def get_sync_history(
        self,
        connection_id: Optional[str] = None,
        limit: int = 50
    ) -> List[SyncLog]:
        """Get synchronization history"""
        logs = self.sync_logs

        if connection_id:
            logs = [l for l in logs if l.connection_id == connection_id]

        # Return most recent
        return sorted(logs, key=lambda x: x.started_at, reverse=True)[:limit]

    def test_connection(self, connection_id: str) -> bool:
        """Test ERP connection"""
        connector = self.get_connector(connection_id)
        return connector is not None

    def get_statistics(self) -> Dict[str, Any]:
        """Get integration statistics"""
        total_syncs = len(self.sync_logs)
        successful_syncs = len([l for l in self.sync_logs if l.status == SyncStatus.COMPLETED])

        total_records = sum(l.records_processed for l in self.sync_logs)
        successful_records = sum(l.records_success for l in self.sync_logs)

        return {
            'total_connections': len(self.connections),
            'active_connections': len([c for c in self.connections.values() if c.enabled]),
            'total_mappings': len(self.mappings),
            'total_syncs': total_syncs,
            'successful_syncs': successful_syncs,
            'failed_syncs': total_syncs - successful_syncs,
            'success_rate': (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0,
            'total_records_processed': total_records,
            'total_records_success': successful_records,
            'last_sync': max([l.started_at for l in self.sync_logs]) if self.sync_logs else None
        }


# Global instance
_erp_engine: Optional[ERPIntegrationEngine] = None


def get_erp_engine(database=None) -> ERPIntegrationEngine:
    """Get global ERP integration engine instance"""
    global _erp_engine

    if _erp_engine is None:
        _erp_engine = ERPIntegrationEngine(database)

    return _erp_engine


def configure_erp_engine(database):
    """Configure ERP integration engine"""
    global _erp_engine
    _erp_engine = ERPIntegrationEngine(database)
