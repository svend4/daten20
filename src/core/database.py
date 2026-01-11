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

# Module logger
logger = get_logger(__name__)


class Database:
    """SQLite database manager"""

    def __init__(self, db_path: str = DATABASE_FILE):
        """
        Initialize database

        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
        logger.info(f"Initializing database at {db_path}")
        self._ensure_db_exists()
        logger.debug("Database initialization complete")

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

                # Create indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_services_name ON services(name)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_services_region ON services(region)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_financial_service ON financial_data(service_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_versions_service ON versions(service_id)')
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

            with sqlite3.connect(self.db_path) as conn:
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

                conn.commit()

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
            with sqlite3.connect(self.db_path) as conn:
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
