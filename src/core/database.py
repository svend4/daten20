"""Database module for storing services and calculations"""

import sqlite3
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from ..models.service import Service
from ..utils.constants import DATABASE_FILE


class Database:
    """SQLite database manager"""

    def __init__(self, db_path: str = DATABASE_FILE):
        """
        Initialize database

        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self) -> None:
        """Ensure database and tables exist"""
        # Create directory if needed
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

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

            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_services_name ON services(name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_services_region ON services(region)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_financial_service ON financial_data(service_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_versions_service ON versions(service_id)')

            conn.commit()

    def create_service(self, service: Service) -> int:
        """
        Create new service in database

        Args:
            service: Service object

        Returns:
            ID of created service
        """
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

            # Save financial data
            cursor.execute('''
                INSERT INTO financial_data (service_id, brutto_rate, calculation_json)
                VALUES (?, ?, ?)
            ''', (
                service_id,
                float(service.financial.brutto_rate),
                json.dumps({}) if not service.cost_breakdown else service.cost_breakdown.to_dict()
            ))

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

            conn.commit()

        service.id = service_id
        return service_id

    def get_service(self, service_id: int) -> Optional[Service]:
        """
        Get service by ID

        Args:
            service_id: Service ID

        Returns:
            Service object or None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT config_json FROM services WHERE id = ?', (service_id,))
            row = cursor.fetchone()

            if row:
                return Service.from_json(row[0])

        return None

    def update_service(self, service: Service) -> bool:
        """
        Update existing service

        Args:
            service: Service object with ID

        Returns:
            True if successful
        """
        if service.id is None:
            return False

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

        return True

    def delete_service(self, service_id: int) -> bool:
        """
        Delete service

        Args:
            service_id: Service ID

        Returns:
            True if successful
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM services WHERE id = ?', (service_id,))
            conn.commit()

        return cursor.rowcount > 0

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

            return services

    def search_services(self, query: str) -> List[Service]:
        """
        Search services by name or target group

        Args:
            query: Search query

        Returns:
            List of matching services
        """
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

            return services

    def get_service_versions(self, service_id: int) -> List[Dict[str, Any]]:
        """
        Get all versions of a service

        Args:
            service_id: Service ID

        Returns:
            List of version records
        """
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

            return versions

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics

        Returns:
            Dictionary with statistics
        """
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

            return {
                'total_services': total_services,
                'by_region': by_region,
                'by_type': by_type,
                'avg_brutto_rate': round(avg_brutto, 2)
            }
