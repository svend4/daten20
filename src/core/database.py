"""Database module for storing services and calculations"""

import sqlite3
import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from ..models.service import Service
from ..utils.constants import DATABASE_FILE
from .logger import get_logger
from .connection_pool import get_connection_pool, ConnectionPool
from .migrations import MigrationManager, register_all_migrations

# Module logger
logger = get_logger(__name__)


class Database:
    """SQLite database manager with connection pooling and migrations"""

    def __init__(self, db_path: str = DATABASE_FILE, pool_size: int = 5):
        """
        Initialize database

        Args:
            db_path: Path to database file
            pool_size: Size of connection pool
        """
        self.db_path = db_path
        logger.info(f"Initializing database at {db_path} with pool size {pool_size}")

        # Initialize connection pool
        self.pool = get_connection_pool(db_path, pool_size)

        # Run migrations
        self._run_migrations()

        # Ensure schema exists (for compatibility)
        self._ensure_db_exists()

        logger.debug("Database initialization complete")

    def _run_migrations(self):
        """Run database migrations."""
        logger.info("Checking database migrations")
        try:
            migration_manager = MigrationManager(self.db_path)
            register_all_migrations(migration_manager)

            current_version = migration_manager.get_current_version()
            pending = migration_manager.get_pending_migrations()

            if pending:
                logger.info(f"Applying {len(pending)} pending migrations")
                migration_manager.migrate_to_latest()
            else:
                logger.info(f"Database is up to date (version {current_version})")

        except Exception as e:
            logger.warning(f"Migration check failed: {e}")
            # Continue anyway for backward compatibility

    def _ensure_db_exists(self) -> None:
        """Ensure database and tables exist"""
        try:
            # Create directory if needed
            db_dir = Path(self.db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Database directory ensured: {db_dir}")

            # Create tables
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Services table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS services (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        target_group TEXT,
                        region TEXT,
                        service_type TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        version INTEGER DEFAULT 1,
                        config_json TEXT NOT NULL
                    )
                ''')
                logger.debug("Services table created/verified")

                # Financial data table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS financial_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        service_id INTEGER NOT NULL,
                        brutto_rate REAL NOT NULL,
                        final_hourly_rate REAL,
                        calculation_json TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
                    )
                ''')
                logger.debug("Financial data table created/verified")

                # Versions table (for version history)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS versions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        service_id INTEGER NOT NULL,
                        version_number INTEGER NOT NULL,
                        config_snapshot TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by TEXT,
                        change_notes TEXT,
                        FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
                    )
                ''')
                logger.debug("Versions table created/verified")

                # Subscriptions table (for BI dashboard)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS subscriptions (
                        id TEXT PRIMARY KEY,
                        tenant_id TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'active',
                        billing_cycle TEXT NOT NULL,
                        amount REAL NOT NULL,
                        currency TEXT DEFAULT 'EUR',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        canceled_at TIMESTAMP NULL,
                        metadata_json TEXT DEFAULT '{}'
                    )
                ''')
                logger.debug("Subscriptions table created/verified")

                # Create indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_services_name ON services(name)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_services_region ON services(region)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_financial_service ON financial_data(service_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_versions_service ON versions(service_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_subscriptions_tenant ON subscriptions(tenant_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_subscriptions_created ON subscriptions(created_at)')
                logger.debug("Database indexes created/verified")

                conn.commit()
                logger.info("Database schema setup complete")
        except Exception as e:
            logger.error(f"Error setting up database schema: {e}", exc_info=True)
            raise

    def create_service(self, service: Service) -> int:
        """
        Create new service in database

        Args:
            service: Service object

        Returns:
            ID of created service
        """
        try:
            logger.info(f"Creating new service: {service.basic_info.service_name}")
            service.created_at = datetime.now()
            service.updated_at = datetime.now()

            # Use connection pool
            with self.pool.get_connection_context() as conn:
                cursor = conn.cursor()

                config_json = service.to_json()

                cursor.execute('''
                    INSERT INTO services (name, target_group, region, service_type, config_json)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    service.basic_info.service_name,
                    service.basic_info.target_group,
                    service.basic_info.region,
                    service.system_settings.service_type,
                    config_json
                ))

                service_id = cursor.lastrowid
                logger.debug(f"Service created with ID: {service_id}")

                # Save financial data
                cursor.execute('''
                    INSERT INTO financial_data (service_id, brutto_rate, calculation_json)
                    VALUES (?, ?, ?)
                ''', (
                    service_id,
                    float(service.financial.brutto_rate),
                    json.dumps({}) if not service.cost_breakdown else service.cost_breakdown.to_dict()
                ))
                logger.debug(f"Financial data saved for service {service_id}")

                # Create initial version
                cursor.execute('''
                    INSERT INTO versions (service_id, version_number, config_snapshot, change_notes)
                    VALUES (?, ?, ?, ?)
                ''', (
                    service_id,
                    1,
                    config_json,
                    "Initial version"
                ))
                logger.debug(f"Initial version created for service {service_id}")

            service.id = service_id
            logger.info(f"Service created successfully: ID={service_id}, name={service.basic_info.service_name}")
            return service_id
        except Exception as e:
            logger.error(f"Error creating service: {e}", exc_info=True)
            raise

    def get_service(self, service_id: int) -> Optional[Service]:
        """
        Get service by ID

        Args:
            service_id: Service ID

        Returns:
            Service object or None
        """
        try:
            logger.debug(f"Retrieving service with ID: {service_id}")

            # Use connection pool
            with self.pool.get_connection_context() as conn:
                cursor = conn.cursor()

                cursor.execute('SELECT config_json FROM services WHERE id = ?', (service_id,))
                row = cursor.fetchone()

                if row:
                    logger.info(f"Service found: ID={service_id}")
                    return Service.from_json(row[0])
                else:
                    logger.warning(f"Service not found: ID={service_id}")

            return None
        except Exception as e:
            logger.error(f"Error retrieving service {service_id}: {e}", exc_info=True)
            raise

    def update_service(self, service: Service) -> bool:
        """
        Update existing service

        Args:
            service: Service object with ID

        Returns:
            True if successful
        """
        if service.id is None:
            logger.warning("Attempted to update service without ID")
            return False

        try:
            logger.info(f"Updating service: ID={service.id}, name={service.basic_info.service_name}")
            service.updated_at = datetime.now()
            service.version += 1

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                config_json = service.to_json()

                cursor.execute('''
                    UPDATE services
                    SET name = ?, target_group = ?, region = ?, service_type = ?,
                        updated_at = ?, version = ?, config_json = ?
                    WHERE id = ?
                ''', (
                    service.basic_info.service_name,
                    service.basic_info.target_group,
                    service.basic_info.region,
                    service.system_settings.service_type,
                    service.updated_at,
                    service.version,
                    config_json,
                    service.id
                ))

                # Create version snapshot
                cursor.execute('''
                    INSERT INTO versions (service_id, version_number, config_snapshot, change_notes)
                    VALUES (?, ?, ?, ?)
                ''', (
                    service.id,
                    service.version,
                    config_json,
                    f"Updated to version {service.version}"
                ))

                conn.commit()

            logger.info(f"Service updated successfully: ID={service.id}, version={service.version}")
            return True
        except Exception as e:
            logger.error(f"Error updating service {service.id}: {e}", exc_info=True)
            raise

    def delete_service(self, service_id: int) -> bool:
        """
        Delete service

        Args:
            service_id: Service ID

        Returns:
            True if successful
        """
        try:
            logger.info(f"Deleting service: ID={service_id}")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM services WHERE id = ?', (service_id,))
                conn.commit()

                deleted = cursor.rowcount > 0
                if deleted:
                    logger.info(f"Service deleted successfully: ID={service_id}")
                else:
                    logger.warning(f"Service not found for deletion: ID={service_id}")

            return deleted
        except Exception as e:
            logger.error(f"Error deleting service {service_id}: {e}", exc_info=True)
            raise

    def list_services(
        self,
        limit: int = 100,
        offset: int = 0,
        region: Optional[str] = None,
        service_type: Optional[str] = None
    ) -> List[Service]:
        """
        List services with optional filters

        Args:
            limit: Maximum number of results
            offset: Offset for pagination
            region: Filter by region
            service_type: Filter by service type

        Returns:
            List of Service objects
        """
        try:
            filters = []
            if region:
                filters.append(f"region={region}")
            if service_type:
                filters.append(f"type={service_type}")

            filter_str = ", ".join(filters) if filters else "no filters"
            logger.debug(f"Listing services: limit={limit}, offset={offset}, {filter_str}")

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                query = 'SELECT config_json FROM services WHERE 1=1'
                params = []

                if region:
                    query += ' AND region = ?'
                    params.append(region)

                if service_type:
                    query += ' AND service_type = ?'
                    params.append(service_type)

                query += ' ORDER BY updated_at DESC LIMIT ? OFFSET ?'
                params.extend([limit, offset])

                cursor.execute(query, params)

                services = []
                for row in cursor.fetchall():
                    services.append(Service.from_json(row[0]))

            logger.info(f"Listed {len(services)} services ({filter_str})")
            return services
        except Exception as e:
            logger.error(f"Error listing services: {e}", exc_info=True)
            raise

    def search_services(self, query: str) -> List[Service]:
        """
        Search services by name or target group

        Args:
            query: Search query

        Returns:
            List of matching services
        """
        try:
            logger.debug(f"Searching services with query: '{query}'")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT config_json FROM services
                    WHERE name LIKE ? OR target_group LIKE ?
                    ORDER BY updated_at DESC
                ''', (f'%{query}%', f'%{query}%'))

                services = []
                for row in cursor.fetchall():
                    services.append(Service.from_json(row[0]))

            logger.info(f"Search found {len(services)} services for query: '{query}'")
            return services
        except Exception as e:
            logger.error(f"Error searching services: {e}", exc_info=True)
            raise

    def get_service_versions(self, service_id: int) -> List[Dict[str, Any]]:
        """
        Get all versions of a service

        Args:
            service_id: Service ID

        Returns:
            List of version records
        """
        try:
            logger.debug(f"Retrieving version history for service: ID={service_id}")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT version_number, created_at, change_notes
                    FROM versions
                    WHERE service_id = ?
                    ORDER BY version_number DESC
                ''', (service_id,))

                versions = []
                for row in cursor.fetchall():
                    versions.append({
                        'version': row[0],
                        'created_at': row[1],
                        'notes': row[2]
                    })

            logger.info(f"Retrieved {len(versions)} versions for service: ID={service_id}")
            return versions
        except Exception as e:
            logger.error(f"Error retrieving service versions: {e}", exc_info=True)
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics

        Returns:
            Dictionary with statistics
        """
        try:
            logger.debug("Retrieving database statistics")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Total services
                cursor.execute('SELECT COUNT(*) FROM services')
                total_services = cursor.fetchone()[0]

                # Services by region
                cursor.execute('SELECT region, COUNT(*) FROM services GROUP BY region')
                by_region = dict(cursor.fetchall())

                # Services by type
                cursor.execute('SELECT service_type, COUNT(*) FROM services GROUP BY service_type')
                by_type = dict(cursor.fetchall())

                # Average brutto rate
                cursor.execute('SELECT AVG(brutto_rate) FROM financial_data')
                avg_brutto = cursor.fetchone()[0] or 0

                stats = {
                    'total_services': total_services,
                    'by_region': by_region,
                    'by_type': by_type,
                    'avg_brutto_rate': round(avg_brutto, 2)
                }

            logger.info(f"Statistics retrieved: {total_services} total services")
            return stats
        except Exception as e:
            logger.error(f"Error retrieving statistics: {e}", exc_info=True)
            raise

    def create_subscription(
        self,
        subscription_id: str,
        tenant_id: str,
        billing_cycle: str,
        amount: float,
        status: str = 'active',
        currency: str = 'EUR',
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create new subscription record

        Args:
            subscription_id: Unique subscription ID
            tenant_id: Tenant/customer ID
            billing_cycle: 'monthly' or 'yearly'
            amount: Subscription amount
            status: Subscription status (default: 'active')
            currency: Currency code (default: 'EUR')
            metadata: Additional metadata

        Returns:
            True if successful
        """
        try:
            logger.info(f"Creating subscription: {subscription_id} for tenant {tenant_id}")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO subscriptions
                    (id, tenant_id, status, billing_cycle, amount, currency, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    subscription_id,
                    tenant_id,
                    status,
                    billing_cycle,
                    amount,
                    currency,
                    json.dumps(metadata or {})
                ))

                conn.commit()

            logger.info(f"Subscription created successfully: {subscription_id}")
            return True
        except sqlite3.IntegrityError as e:
            logger.warning(f"Subscription {subscription_id} already exists: {e}")
            return False
        except Exception as e:
            logger.error(f"Error creating subscription: {e}", exc_info=True)
            raise

    def get_subscriptions(
        self,
        tenant_id: Optional[str] = None,
        status: Optional[str] = None,
        as_of_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get subscriptions with optional filters

        Args:
            tenant_id: Filter by tenant ID
            status: Filter by status
            as_of_date: Get subscriptions as of this date

        Returns:
            List of subscription dictionaries
        """
        try:
            filters_log = []
            if tenant_id:
                filters_log.append(f"tenant={tenant_id}")
            if status:
                filters_log.append(f"status={status}")
            if as_of_date:
                filters_log.append(f"as_of={as_of_date}")

            filter_str = ", ".join(filters_log) if filters_log else "no filters"
            logger.debug(f"Fetching subscriptions: {filter_str}")

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                query = 'SELECT id, tenant_id, status, billing_cycle, amount, currency, created_at, metadata_json FROM subscriptions WHERE 1=1'
                params = []

                if tenant_id:
                    query += ' AND tenant_id = ?'
                    params.append(tenant_id)

                if status:
                    query += ' AND status = ?'
                    params.append(status)

                if as_of_date:
                    query += ' AND created_at <= ?'
                    params.append(as_of_date.isoformat())

                query += ' ORDER BY created_at DESC'

                cursor.execute(query, params)

                subscriptions = []
                for row in cursor.fetchall():
                    subscriptions.append({
                        'id': row[0],
                        'tenant_id': row[1],
                        'status': row[2],
                        'billing_cycle': row[3],
                        'amount': row[4],
                        'currency': row[5],
                        'created_at': row[6],
                        'metadata': json.loads(row[7]) if row[7] else {}
                    })

            logger.info(f"Retrieved {len(subscriptions)} subscriptions")
            return subscriptions
        except Exception as e:
            logger.error(f"Error fetching subscriptions: {e}", exc_info=True)
            raise

    def update_subscription_status(
        self,
        subscription_id: str,
        status: str
    ) -> bool:
        """
        Update subscription status

        Args:
            subscription_id: Subscription ID
            status: New status

        Returns:
            True if successful
        """
        try:
            logger.info(f"Updating subscription {subscription_id} status to: {status}")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    UPDATE subscriptions
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (status, subscription_id))

                conn.commit()
                updated = cursor.rowcount > 0

                if updated:
                    logger.info(f"Subscription {subscription_id} updated successfully")
                else:
                    logger.warning(f"Subscription {subscription_id} not found")

                return updated
        except Exception as e:
            logger.error(f"Error updating subscription: {e}", exc_info=True)
            raise

    def delete_subscription(self, subscription_id: str) -> bool:
        """
        Delete subscription

        Args:
            subscription_id: Subscription ID

        Returns:
            True if deleted
        """
        try:
            logger.info(f"Deleting subscription: {subscription_id}")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM subscriptions WHERE id = ?', (subscription_id,))
                conn.commit()

                deleted = cursor.rowcount > 0
                if deleted:
                    logger.info(f"Subscription deleted: {subscription_id}")
                else:
                    logger.warning(f"Subscription not found: {subscription_id}")

                return deleted
        except Exception as e:
            logger.error(f"Error deleting subscription: {e}", exc_info=True)
            raise

    def initialize_sample_subscriptions(self, tenant_id: str = "tenant_001") -> int:
        """
        Initialize sample subscription data for testing

        Args:
            tenant_id: Tenant ID for sample data

        Returns:
            Number of subscriptions created
        """
        logger.info(f"Initializing sample subscriptions for tenant: {tenant_id}")

        sample_data = [
            {
                'id': f'sub_{tenant_id}_monthly_1',
                'billing_cycle': 'monthly',
                'amount': 99.00,
                'status': 'active',
                'metadata': {'plan': 'professional', 'users': 5}
            },
            {
                'id': f'sub_{tenant_id}_monthly_2',
                'billing_cycle': 'monthly',
                'amount': 49.00,
                'status': 'active',
                'metadata': {'plan': 'basic', 'users': 2}
            },
            {
                'id': f'sub_{tenant_id}_yearly_1',
                'billing_cycle': 'yearly',
                'amount': 990.00,
                'status': 'active',
                'metadata': {'plan': 'professional', 'users': 5, 'discount': '15%'}
            },
            {
                'id': f'sub_{tenant_id}_yearly_2',
                'billing_cycle': 'yearly',
                'amount': 490.00,
                'status': 'active',
                'metadata': {'plan': 'basic', 'users': 2, 'discount': '15%'}
            },
            {
                'id': f'sub_{tenant_id}_monthly_canceled',
                'billing_cycle': 'monthly',
                'amount': 199.00,
                'status': 'canceled',
                'metadata': {'plan': 'enterprise', 'users': 20}
            },
        ]

        created_count = 0
        for sub in sample_data:
            try:
                success = self.create_subscription(
                    subscription_id=sub['id'],
                    tenant_id=tenant_id,
                    billing_cycle=sub['billing_cycle'],
                    amount=sub['amount'],
                    status=sub['status'],
                    metadata=sub['metadata']
                )
                if success:
                    created_count += 1
            except Exception as e:
                logger.warning(f"Failed to create sample subscription {sub['id']}: {e}")

        logger.info(f"Created {created_count} sample subscriptions")
        return created_count


# Alias for backward compatibility
DocumentDatabase = Database
