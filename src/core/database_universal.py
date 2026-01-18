"""
Universal Database Module with PostgreSQL, MySQL and SQLite Support

This module provides a unified database interface that works with:
- SQLite (default, file-based)
- PostgreSQL (production)
- MySQL/MariaDB (production)

Uses SQLAlchemy ORM for database-agnostic operations.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

from ..models.service import Service
from .db_models import (
    Base,
    FinancialData,
    Service as ServiceModel,
    Subscription,
    Version,
)
from .logger import get_logger

# Module logger
logger = get_logger(__name__)


class UniversalDatabase:
    """
    Universal database manager supporting SQLite, PostgreSQL, and MySQL.

    Features:
    - Multi-database support (SQLite, PostgreSQL, MySQL)
    - Connection pooling
    - Automatic schema creation
    - ORM-based operations
    - Transaction management
    """

    def __init__(
        self,
        database_url: Optional[str] = None,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        echo: bool = False,
    ):
        """
        Initialize universal database connection.

        Args:
            database_url: Database URL (e.g., 'postgresql://user:pass@host/db')
                         If None, uses 'data/db/services.db' (SQLite)
            pool_size: Size of connection pool
            max_overflow: Maximum pool overflow
            pool_timeout: Connection timeout in seconds
            echo: Enable SQL echo (debug)
        """
        # Set default SQLite database if no URL provided
        if database_url is None:
            db_path = Path(__file__).parent.parent.parent / "data" / "db" / "services.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            database_url = f"sqlite:///{db_path}"

        self.database_url = database_url
        self.db_type = self._detect_database_type(database_url)

        logger.info(f"Initializing {self.db_type.upper()} database")
        logger.debug(f"Database URL: {self._sanitize_url(database_url)}")

        # Create engine with appropriate pool
        self.engine = self._create_engine(
            database_url, pool_size, max_overflow, pool_timeout, echo
        )

        # Create session factory
        self.Session = sessionmaker(bind=self.engine)

        # Setup database
        self._setup_database()

        logger.info(f"{self.db_type.upper()} database initialized successfully")

    def _detect_database_type(self, url: str) -> str:
        """Detect database type from URL."""
        parsed = urlparse(url)
        scheme = parsed.scheme.split('+')[0]  # Handle postgresql+psycopg2

        if scheme in ('postgresql', 'postgres'):
            return 'postgresql'
        elif scheme in ('mysql', 'mariadb'):
            return 'mysql'
        elif scheme == 'sqlite':
            return 'sqlite'
        else:
            logger.warning(f"Unknown database scheme: {scheme}, defaulting to SQLite")
            return 'sqlite'

    def _sanitize_url(self, url: str) -> str:
        """Sanitize database URL for logging (hide passwords)."""
        parsed = urlparse(url)
        if parsed.password:
            return url.replace(parsed.password, "***")
        return url

    def _create_engine(
        self, url: str, pool_size: int, max_overflow: int, pool_timeout: int, echo: bool
    ):
        """Create SQLAlchemy engine with appropriate configuration."""

        # Engine arguments
        engine_args = {
            'echo': echo,
            'future': True,  # SQLAlchemy 2.0 style
        }

        # Configure pooling based on database type
        if self.db_type == 'sqlite':
            # SQLite: Use NullPool for file-based database
            engine_args['poolclass'] = NullPool
            engine_args['connect_args'] = {
                'check_same_thread': False,
                'timeout': pool_timeout,
            }
        else:
            # PostgreSQL/MySQL: Use QueuePool
            engine_args['poolclass'] = QueuePool
            engine_args['pool_size'] = pool_size
            engine_args['max_overflow'] = max_overflow
            engine_args['pool_timeout'] = pool_timeout
            engine_args['pool_pre_ping'] = True  # Verify connections

        try:
            engine = create_engine(url, **engine_args)

            # Configure SQLite optimizations
            if self.db_type == 'sqlite':
                @event.listens_for(engine, "connect")
                def set_sqlite_pragma(dbapi_conn, connection_record):
                    cursor = dbapi_conn.cursor()
                    # Enable WAL mode for better concurrency
                    cursor.execute("PRAGMA journal_mode=WAL")
                    # Enable foreign keys
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.close()

            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            logger.info(f"Database engine created successfully: {self.db_type}")
            return engine

        except Exception as e:
            logger.error(f"Failed to create database engine: {e}", exc_info=True)
            raise

    def _setup_database(self):
        """Create tables and schema if they don't exist."""
        try:
            # Create all tables defined in Base metadata
            Base.metadata.create_all(self.engine)

            # Verify tables exist
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()

            expected_tables = ['services', 'financial_data', 'versions', 'subscriptions']
            for table in expected_tables:
                if table in tables:
                    logger.debug(f"Table '{table}' verified")
                else:
                    logger.warning(f"Table '{table}' not found!")

            logger.info("Database schema setup complete")

        except Exception as e:
            logger.error(f"Error setting up database schema: {e}", exc_info=True)
            raise

    def get_session(self) -> Session:
        """
        Get a new database session.

        Returns:
            SQLAlchemy Session object

        Usage:
            with db.get_session() as session:
                # Use session
                pass
        """
        return self.Session()

    def create_service(self, service: Service) -> int:
        """
        Create new service in database.

        Args:
            service: Service object

        Returns:
            ID of created service
        """
        try:
            logger.info(f"Creating new service: {service.basic_info.service_name}")

            with self.get_session() as session:
                # Create service model
                service_model = ServiceModel(
                    name=service.basic_info.service_name,
                    target_group=service.basic_info.target_group,
                    region=service.basic_info.region,
                    service_type=service.system_settings.service_type,
                    config_json=service.to_json(),
                    version=1,
                )

                session.add(service_model)
                session.flush()  # Get ID without committing

                service_id = service_model.id

                # Create financial data
                financial_data = FinancialData(
                    service_id=service_id,
                    brutto_rate=float(service.financial.brutto_rate),
                    calculation_json=json.dumps(
                        {} if not service.cost_breakdown else service.cost_breakdown.to_dict()
                    ),
                )
                session.add(financial_data)

                # Create initial version
                version = Version(
                    service_id=service_id,
                    version_number=1,
                    config_snapshot=service.to_json(),
                    change_notes="Initial version",
                )
                session.add(version)

                session.commit()

            service.id = service_id
            logger.info(f"Service created successfully: ID={service_id}")
            return service_id

        except SQLAlchemyError as e:
            logger.error(f"Database error creating service: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Error creating service: {e}", exc_info=True)
            raise

    def get_service(self, service_id: int) -> Optional[Service]:
        """
        Get service by ID.

        Args:
            service_id: Service ID

        Returns:
            Service object or None
        """
        try:
            logger.debug(f"Retrieving service with ID: {service_id}")

            with self.get_session() as session:
                service_model = session.get(ServiceModel, service_id)

                if service_model:
                    logger.info(f"Service found: ID={service_id}")
                    return Service.from_json(service_model.config_json)
                else:
                    logger.warning(f"Service not found: ID={service_id}")
                    return None

        except Exception as e:
            logger.error(f"Error retrieving service {service_id}: {e}", exc_info=True)
            raise

    def update_service(self, service: Service) -> bool:
        """
        Update existing service.

        Args:
            service: Service object with ID

        Returns:
            True if successful
        """
        if service.id is None:
            logger.warning("Attempted to update service without ID")
            return False

        try:
            logger.info(f"Updating service: ID={service.id}")

            with self.get_session() as session:
                service_model = session.get(ServiceModel, service.id)

                if not service_model:
                    logger.warning(f"Service not found for update: ID={service.id}")
                    return False

                # Update fields
                service.version = service_model.version + 1
                service.updated_at = datetime.now()

                service_model.name = service.basic_info.service_name
                service_model.target_group = service.basic_info.target_group
                service_model.region = service.basic_info.region
                service_model.service_type = service.system_settings.service_type
                service_model.updated_at = service.updated_at
                service_model.version = service.version
                service_model.config_json = service.to_json()

                # Create version snapshot
                version = Version(
                    service_id=service.id,
                    version_number=service.version,
                    config_snapshot=service.to_json(),
                    change_notes=f"Updated to version {service.version}",
                )
                session.add(version)

                session.commit()

            logger.info(f"Service updated successfully: ID={service.id}, version={service.version}")
            return True

        except Exception as e:
            logger.error(f"Error updating service {service.id}: {e}", exc_info=True)
            raise

    def delete_service(self, service_id: int) -> bool:
        """
        Delete service.

        Args:
            service_id: Service ID

        Returns:
            True if successful
        """
        try:
            logger.info(f"Deleting service: ID={service_id}")

            with self.get_session() as session:
                service_model = session.get(ServiceModel, service_id)

                if not service_model:
                    logger.warning(f"Service not found for deletion: ID={service_id}")
                    return False

                session.delete(service_model)
                session.commit()

            logger.info(f"Service deleted successfully: ID={service_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting service {service_id}: {e}", exc_info=True)
            raise

    def list_services(
        self,
        limit: int = 100,
        offset: int = 0,
        region: Optional[str] = None,
        service_type: Optional[str] = None,
    ) -> List[Service]:
        """
        List services with pagination and optional filters.

        Args:
            limit: Maximum number of results
            offset: Offset for pagination
            region: Filter by region
            service_type: Filter by service type

        Returns:
            List of Service objects
        """
        try:
            logger.debug(f"Listing services: limit={limit}, offset={offset}")

            with self.get_session() as session:
                query = session.query(ServiceModel)

                # Apply filters
                if region:
                    query = query.filter(ServiceModel.region == region)
                if service_type:
                    query = query.filter(ServiceModel.service_type == service_type)

                # Order and paginate
                query = query.order_by(ServiceModel.updated_at.desc())
                query = query.limit(limit).offset(offset)

                # Execute query
                service_models = query.all()

                # Convert to Service objects
                services = [
                    Service.from_json(model.config_json)
                    for model in service_models
                ]

            logger.info(f"Listed {len(services)} services")
            return services

        except Exception as e:
            logger.error(f"Error listing services: {e}", exc_info=True)
            raise

    def count_services(
        self, region: Optional[str] = None, service_type: Optional[str] = None
    ) -> int:
        """
        Count total services with optional filters.

        Args:
            region: Filter by region
            service_type: Filter by service type

        Returns:
            Total count
        """
        try:
            with self.get_session() as session:
                query = session.query(ServiceModel)

                if region:
                    query = query.filter(ServiceModel.region == region)
                if service_type:
                    query = query.filter(ServiceModel.service_type == service_type)

                count = query.count()

            logger.debug(f"Counted {count} services")
            return count

        except Exception as e:
            logger.error(f"Error counting services: {e}")
            return 0

    def search_services(self, query: str) -> List[Service]:
        """
        Search services by name or target group.

        Args:
            query: Search query

        Returns:
            List of matching services
        """
        try:
            logger.debug(f"Searching services with query: '{query}'")

            with self.get_session() as session:
                # Use LIKE for pattern matching (works on all databases)
                search_pattern = f"%{query}%"

                service_models = (
                    session.query(ServiceModel)
                    .filter(
                        (ServiceModel.name.like(search_pattern)) |
                        (ServiceModel.target_group.like(search_pattern))
                    )
                    .order_by(ServiceModel.updated_at.desc())
                    .all()
                )

                services = [
                    Service.from_json(model.config_json)
                    for model in service_models
                ]

            logger.info(f"Search found {len(services)} services")
            return services

        except Exception as e:
            logger.error(f"Error searching services: {e}", exc_info=True)
            raise

    def get_service_versions(self, service_id: int) -> List[Dict[str, Any]]:
        """
        Get all versions of a service.

        Args:
            service_id: Service ID

        Returns:
            List of version records
        """
        try:
            logger.debug(f"Retrieving version history for service: ID={service_id}")

            with self.get_session() as session:
                version_models = (
                    session.query(Version)
                    .filter(Version.service_id == service_id)
                    .order_by(Version.version_number.desc())
                    .all()
                )

                versions = [
                    {
                        "version": v.version_number,
                        "created_at": v.created_at.isoformat() if v.created_at else None,
                        "notes": v.change_notes,
                    }
                    for v in version_models
                ]

            logger.info(f"Retrieved {len(versions)} versions for service: ID={service_id}")
            return versions

        except Exception as e:
            logger.error(f"Error retrieving service versions: {e}", exc_info=True)
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns:
            Dictionary with statistics
        """
        try:
            logger.debug("Retrieving database statistics")

            with self.get_session() as session:
                # Total services
                total_services = session.query(ServiceModel).count()

                # Services by region
                by_region = {}
                for region, count in (
                    session.query(ServiceModel.region, text('COUNT(*)'))
                    .group_by(ServiceModel.region)
                    .all()
                ):
                    by_region[region] = count

                # Services by type
                by_type = {}
                for service_type, count in (
                    session.query(ServiceModel.service_type, text('COUNT(*)'))
                    .group_by(ServiceModel.service_type)
                    .all()
                ):
                    by_type[service_type] = count

                # Average brutto rate
                avg_result = session.query(text('AVG(brutto_rate)')).select_from(FinancialData).scalar()
                avg_brutto = round(float(avg_result), 2) if avg_result else 0.0

                stats = {
                    "total_services": total_services,
                    "by_region": by_region,
                    "by_type": by_type,
                    "avg_brutto_rate": avg_brutto,
                    "database_type": self.db_type,
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
        status: str = "active",
        currency: str = "EUR",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Create new subscription record."""
        try:
            logger.info(f"Creating subscription: {subscription_id} for tenant {tenant_id}")

            with self.get_session() as session:
                subscription = Subscription(
                    id=subscription_id,
                    tenant_id=tenant_id,
                    status=status,
                    billing_cycle=billing_cycle,
                    amount=amount,
                    currency=currency,
                    metadata_json=json.dumps(metadata or {}),
                )

                session.add(subscription)
                session.commit()

            logger.info(f"Subscription created successfully: {subscription_id}")
            return True

        except SQLAlchemyError as e:
            logger.warning(f"Subscription {subscription_id} may already exist: {e}")
            return False
        except Exception as e:
            logger.error(f"Error creating subscription: {e}", exc_info=True)
            raise

    def health_check(self) -> Dict[str, Any]:
        """
        Perform database health check.

        Returns:
            Health status dictionary
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            return {
                "status": "healthy",
                "database_type": self.db_type,
                "url": self._sanitize_url(self.database_url),
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "database_type": self.db_type,
                "error": str(e),
            }

    def close(self):
        """Close database connections."""
        logger.info("Closing database connections")
        self.engine.dispose()
        logger.info("Database connections closed")


# Factory function for backward compatibility
def get_database(database_url: Optional[str] = None) -> UniversalDatabase:
    """
    Factory function to create database instance.

    Args:
        database_url: Database URL (optional)

    Returns:
        UniversalDatabase instance
    """
    return UniversalDatabase(database_url=database_url)


# Alias for backward compatibility
Database = UniversalDatabase
