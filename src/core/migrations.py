"""
Database Migration System

Manages database schema versions and migrations for safe upgrades.
"""

import sqlite3
import logging
from typing import List, Callable, Dict
from datetime import datetime
from pathlib import Path

logger = logging.getLogger('dms.migrations')


class Migration:
    """Single database migration."""

    def __init__(self, version: int, description: str,
                 up: Callable[[sqlite3.Connection], None],
                 down: Callable[[sqlite3.Connection], None] = None):
        """
        Initialize migration.

        Args:
            version: Migration version number
            description: Migration description
            up: Function to apply migration
            down: Function to rollback migration (optional)
        """
        self.version = version
        self.description = description
        self.up = up
        self.down = down

    def apply(self, conn: sqlite3.Connection):
        """Apply migration."""
        logger.info(f"Applying migration {self.version}: {self.description}")
        self.up(conn)

    def rollback(self, conn: sqlite3.Connection):
        """Rollback migration."""
        if self.down is None:
            raise ValueError(f"Migration {self.version} has no rollback defined")
        logger.info(f"Rolling back migration {self.version}: {self.description}")
        self.down(conn)


class MigrationManager:
    """Manages database migrations."""

    def __init__(self, db_path: str):
        """
        Initialize migration manager.

        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
        self.migrations: List[Migration] = []
        self._ensure_migrations_table()

    def _ensure_migrations_table(self):
        """Ensure migrations tracking table exists."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    description TEXT NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    execution_time_ms INTEGER
                )
            ''')
            conn.commit()
            logger.debug("Migrations table ensured")

    def register_migration(self, migration: Migration):
        """
        Register a migration.

        Args:
            migration: Migration to register
        """
        self.migrations.append(migration)
        self.migrations.sort(key=lambda m: m.version)
        logger.debug(f"Registered migration {migration.version}: {migration.description}")

    def get_current_version(self) -> int:
        """
        Get current database schema version.

        Returns:
            Current version number (0 if no migrations applied)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT MAX(version) FROM schema_migrations')
            result = cursor.fetchone()[0]
            return result if result is not None else 0

    def get_pending_migrations(self) -> List[Migration]:
        """
        Get list of pending migrations.

        Returns:
            List of migrations not yet applied
        """
        current_version = self.get_current_version()
        return [m for m in self.migrations if m.version > current_version]

    def apply_migration(self, migration: Migration) -> bool:
        """
        Apply a single migration.

        Args:
            migration: Migration to apply

        Returns:
            True if successful
        """
        try:
            start_time = datetime.now()

            with sqlite3.connect(self.db_path) as conn:
                # Apply migration
                migration.apply(conn)

                # Record migration
                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO schema_migrations (version, description, execution_time_ms)
                    VALUES (?, ?, ?)
                ''', (migration.version, migration.description, execution_time))

                conn.commit()

            logger.info(
                f"Migration {migration.version} applied successfully "
                f"({execution_time}ms)"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to apply migration {migration.version}: {e}", exc_info=True)
            return False

    def migrate_to_latest(self) -> bool:
        """
        Migrate database to latest version.

        Returns:
            True if all migrations successful
        """
        pending = self.get_pending_migrations()

        if not pending:
            logger.info("Database is up to date")
            return True

        logger.info(f"Applying {len(pending)} pending migrations")

        for migration in pending:
            if not self.apply_migration(migration):
                logger.error(f"Migration {migration.version} failed, stopping")
                return False

        logger.info("All migrations applied successfully")
        return True

    def rollback_to_version(self, target_version: int) -> bool:
        """
        Rollback database to specific version.

        Args:
            target_version: Target version number

        Returns:
            True if successful
        """
        current_version = self.get_current_version()

        if target_version >= current_version:
            logger.warning(f"Already at or below version {target_version}")
            return True

        # Find migrations to rollback (in reverse order)
        to_rollback = [
            m for m in reversed(self.migrations)
            if target_version < m.version <= current_version
        ]

        logger.info(f"Rolling back {len(to_rollback)} migrations")

        for migration in to_rollback:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    migration.rollback(conn)

                    # Remove from migrations table
                    cursor = conn.cursor()
                    cursor.execute(
                        'DELETE FROM schema_migrations WHERE version = ?',
                        (migration.version,)
                    )
                    conn.commit()

                logger.info(f"Rolled back migration {migration.version}")

            except Exception as e:
                logger.error(f"Failed to rollback migration {migration.version}: {e}")
                return False

        logger.info(f"Successfully rolled back to version {target_version}")
        return True

    def get_migration_history(self) -> List[Dict]:
        """
        Get migration history.

        Returns:
            List of applied migrations with metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT version, description, applied_at, execution_time_ms
                FROM schema_migrations
                ORDER BY version
            ''')
            return [dict(row) for row in cursor.fetchall()]

    def print_status(self):
        """Print migration status."""
        current_version = self.get_current_version()
        pending = self.get_pending_migrations()

        print("\n" + "="*60)
        print("DATABASE MIGRATION STATUS")
        print("="*60)
        print(f"\nCurrent Version: {current_version}")
        print(f"Latest Version:  {max((m.version for m in self.migrations), default=0)}")
        print(f"Pending:         {len(pending)} migrations")

        if pending:
            print("\nPending Migrations:")
            for migration in pending:
                print(f"  [{migration.version}] {migration.description}")

        print("\nMigration History:")
        history = self.get_migration_history()
        if history:
            for record in history:
                print(f"  [{record['version']}] {record['description']}")
                print(f"      Applied: {record['applied_at']} ({record['execution_time_ms']}ms)")
        else:
            print("  No migrations applied yet")

        print("="*60 + "\n")


# ==================== MIGRATION DEFINITIONS ====================

def register_all_migrations(manager: MigrationManager):
    """Register all application migrations."""

    # Migration 1: Initial schema
    def migration_1_up(conn: sqlite3.Connection):
        """Create initial tables."""
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

        # Versions table
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

    manager.register_migration(Migration(
        version=1,
        description="Initial database schema",
        up=migration_1_up
    ))

    # Migration 2: Add subscriptions table
    def migration_2_up(conn: sqlite3.Connection):
        """Add subscriptions table for BI dashboard."""
        cursor = conn.cursor()
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
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_subscriptions_tenant ON subscriptions(tenant_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_subscriptions_created ON subscriptions(created_at)')

    def migration_2_down(conn: sqlite3.Connection):
        """Remove subscriptions table."""
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS subscriptions')

    manager.register_migration(Migration(
        version=2,
        description="Add subscriptions table",
        up=migration_2_up,
        down=migration_2_down
    ))

    # Migration 3: Add full-text search
    def migration_3_up(conn: sqlite3.Connection):
        """Add full-text search capability."""
        cursor = conn.cursor()
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS services_fts
            USING fts5(name, target_group, content='services', content_rowid='id')
        ''')

        # Populate FTS table
        cursor.execute('''
            INSERT INTO services_fts(rowid, name, target_group)
            SELECT id, name, target_group FROM services
        ''')

    def migration_3_down(conn: sqlite3.Connection):
        """Remove full-text search."""
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS services_fts')

    manager.register_migration(Migration(
        version=3,
        description="Add full-text search",
        up=migration_3_up,
        down=migration_3_down
    ))

    logger.info(f"Registered {len(manager.migrations)} migrations")


# CLI for migration management
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Database migration manager")
    parser.add_argument('--db', default='data/dms.db', help='Database path')
    parser.add_argument('command', choices=['status', 'migrate', 'rollback'],
                       help='Migration command')
    parser.add_argument('--version', type=int, help='Target version for rollback')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create manager and register migrations
    manager = MigrationManager(args.db)
    register_all_migrations(manager)

    # Execute command
    if args.command == 'status':
        manager.print_status()
    elif args.command == 'migrate':
        success = manager.migrate_to_latest()
        exit(0 if success else 1)
    elif args.command == 'rollback':
        if args.version is None:
            print("Error: --version required for rollback")
            exit(1)
        success = manager.rollback_to_version(args.version)
        exit(0 if success else 1)
