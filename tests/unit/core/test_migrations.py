"""
Tests for database migration system.
"""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from src.core.migrations import Migration, MigrationManager, register_all_migrations


@pytest.fixture
def temp_db():
    """Create temporary database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    yield db_path
    # Cleanup
    try:
        Path(db_path).unlink()
    except:
        pass


class TestMigration:
    """Tests for Migration class."""

    def test_migration_creation(self):
        """Test creating migration."""

        def up(conn):
            pass

        def down(conn):
            pass

        migration = Migration(1, "Test migration", up, down)
        assert migration.version == 1
        assert migration.description == "Test migration"
        assert migration.up is up
        assert migration.down is down

    def test_migration_without_down(self):
        """Test migration without rollback."""

        def up(conn):
            pass

        migration = Migration(1, "Test", up)
        assert migration.down is None

    def test_apply_migration(self, temp_db):
        """Test applying migration."""
        executed = []

        def up(conn):
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test (id INTEGER)")
            executed.append("up")

        migration = Migration(1, "Create test table", up)

        with sqlite3.connect(temp_db) as conn:
            migration.apply(conn)

        assert "up" in executed

        # Verify table created
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test'")
            assert cursor.fetchone() is not None

    def test_rollback_migration(self, temp_db):
        """Test rolling back migration."""

        def up(conn):
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test (id INTEGER)")

        def down(conn):
            cursor = conn.cursor()
            cursor.execute("DROP TABLE test")

        migration = Migration(1, "Test", up, down)

        with sqlite3.connect(temp_db) as conn:
            migration.apply(conn)
            migration.rollback(conn)

        # Verify table removed
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test'")
            assert cursor.fetchone() is None

    def test_rollback_without_down_raises_error(self):
        """Test rollback raises error if no down function."""

        def up(conn):
            pass

        migration = Migration(1, "Test", up)

        with pytest.raises(ValueError) as exc:
            with sqlite3.connect(":memory:") as conn:
                migration.rollback(conn)

        assert "no rollback defined" in str(exc.value)


class TestMigrationManager:
    """Tests for MigrationManager class."""

    def test_manager_initialization(self, temp_db):
        """Test manager initialization."""
        manager = MigrationManager(temp_db)
        assert manager.db_path == temp_db

        # Verify migrations table created
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'")
            assert cursor.fetchone() is not None

    def test_register_migration(self, temp_db):
        """Test registering migration."""
        manager = MigrationManager(temp_db)

        def up(conn):
            pass

        migration = Migration(1, "Test", up)
        manager.register_migration(migration)

        assert len(manager.migrations) == 1
        assert manager.migrations[0] is migration

    def test_migrations_sorted_by_version(self, temp_db):
        """Test migrations are sorted by version."""
        manager = MigrationManager(temp_db)

        def up(conn):
            pass

        manager.register_migration(Migration(3, "Third", up))
        manager.register_migration(Migration(1, "First", up))
        manager.register_migration(Migration(2, "Second", up))

        assert [m.version for m in manager.migrations] == [1, 2, 3]

    def test_get_current_version_empty_db(self, temp_db):
        """Test getting version from empty database."""
        manager = MigrationManager(temp_db)
        assert manager.get_current_version() == 0

    def test_get_current_version_after_migration(self, temp_db):
        """Test getting version after migrations."""
        manager = MigrationManager(temp_db)

        def up(conn):
            pass

        manager.register_migration(Migration(1, "Test", up))
        manager.apply_migration(manager.migrations[0])

        assert manager.get_current_version() == 1

    def test_get_pending_migrations(self, temp_db):
        """Test getting pending migrations."""
        manager = MigrationManager(temp_db)

        def up(conn):
            pass

        manager.register_migration(Migration(1, "First", up))
        manager.register_migration(Migration(2, "Second", up))
        manager.register_migration(Migration(3, "Third", up))

        # Initially all pending
        pending = manager.get_pending_migrations()
        assert len(pending) == 3

        # Apply first migration
        manager.apply_migration(manager.migrations[0])

        # Now only 2 pending
        pending = manager.get_pending_migrations()
        assert len(pending) == 2
        assert pending[0].version == 2
        assert pending[1].version == 3

    def test_apply_migration(self, temp_db):
        """Test applying single migration."""
        manager = MigrationManager(temp_db)

        def up(conn):
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test (id INTEGER)")

        migration = Migration(1, "Create test table", up)
        manager.register_migration(migration)

        success = manager.apply_migration(migration)
        assert success is True

        # Verify migration recorded
        assert manager.get_current_version() == 1

        # Verify table created
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test'")
            assert cursor.fetchone() is not None

    def test_apply_migration_records_execution_time(self, temp_db):
        """Test migration execution time is recorded."""
        manager = MigrationManager(temp_db)

        def up(conn):
            pass

        migration = Migration(1, "Test", up)
        manager.register_migration(migration)
        manager.apply_migration(migration)

        history = manager.get_migration_history()
        assert len(history) == 1
        assert "execution_time_ms" in history[0]
        assert history[0]["execution_time_ms"] >= 0

    def test_migrate_to_latest(self, temp_db):
        """Test migrating to latest version."""
        manager = MigrationManager(temp_db)

        def up1(conn):
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE table1 (id INTEGER)")

        def up2(conn):
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE table2 (id INTEGER)")

        manager.register_migration(Migration(1, "First", up1))
        manager.register_migration(Migration(2, "Second", up2))

        success = manager.migrate_to_latest()
        assert success is True

        # Verify both migrations applied
        assert manager.get_current_version() == 2

        # Verify both tables created
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cursor.fetchall()}
            assert "table1" in tables
            assert "table2" in tables

    def test_migrate_to_latest_already_up_to_date(self, temp_db):
        """Test migrating when already up to date."""
        manager = MigrationManager(temp_db)

        def up(conn):
            pass

        migration = Migration(1, "Test", up)
        manager.register_migration(migration)

        # Apply migration
        manager.migrate_to_latest()

        # Try again - should succeed but do nothing
        success = manager.migrate_to_latest()
        assert success is True

    def test_rollback_to_version(self, temp_db):
        """Test rolling back to specific version."""
        manager = MigrationManager(temp_db)

        def up1(conn):
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE table1 (id INTEGER)")

        def down1(conn):
            cursor = conn.cursor()
            cursor.execute("DROP TABLE table1")

        def up2(conn):
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE table2 (id INTEGER)")

        def down2(conn):
            cursor = conn.cursor()
            cursor.execute("DROP TABLE table2")

        manager.register_migration(Migration(1, "First", up1, down1))
        manager.register_migration(Migration(2, "Second", up2, down2))

        # Apply both
        manager.migrate_to_latest()
        assert manager.get_current_version() == 2

        # Rollback to version 1
        success = manager.rollback_to_version(1)
        assert success is True
        assert manager.get_current_version() == 1

        # Verify table2 removed but table1 remains
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cursor.fetchall()}
            assert "table1" in tables
            assert "table2" not in tables

    def test_get_migration_history(self, temp_db):
        """Test getting migration history."""
        manager = MigrationManager(temp_db)

        def up(conn):
            pass

        manager.register_migration(Migration(1, "First migration", up))
        manager.register_migration(Migration(2, "Second migration", up))

        manager.migrate_to_latest()

        history = manager.get_migration_history()
        assert len(history) == 2
        assert history[0]["version"] == 1
        assert history[0]["description"] == "First migration"
        assert history[1]["version"] == 2
        assert history[1]["description"] == "Second migration"

    def test_print_status(self, temp_db, capsys):
        """Test printing migration status."""
        manager = MigrationManager(temp_db)

        def up(conn):
            pass

        manager.register_migration(Migration(1, "Test migration", up))

        manager.print_status()

        captured = capsys.readouterr()
        assert "DATABASE MIGRATION STATUS" in captured.out
        assert "Current Version: 0" in captured.out
        assert "Latest Version:  1" in captured.out
        assert "Pending:         1 migrations" in captured.out


class TestRegisteredMigrations:
    """Tests for application-specific migrations."""

    def test_register_all_migrations(self, temp_db):
        """Test registering all application migrations."""
        manager = MigrationManager(temp_db)
        register_all_migrations(manager)

        # Should have registered migrations
        assert len(manager.migrations) > 0

    def test_migration_1_creates_base_schema(self, temp_db):
        """Test migration 1 creates base schema."""
        manager = MigrationManager(temp_db)
        register_all_migrations(manager)

        # Apply first migration
        manager.apply_migration(manager.migrations[0])

        # Verify tables created
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cursor.fetchall()}

            assert "services" in tables
            assert "financial_data" in tables
            assert "versions" in tables

    def test_migration_2_adds_subscriptions(self, temp_db):
        """Test migration 2 adds subscriptions table."""
        manager = MigrationManager(temp_db)
        register_all_migrations(manager)

        # Apply first two migrations
        manager.apply_migration(manager.migrations[0])
        manager.apply_migration(manager.migrations[1])

        # Verify subscriptions table exists
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='subscriptions'")
            assert cursor.fetchone() is not None

    def test_migration_2_rollback(self, temp_db):
        """Test migration 2 can be rolled back."""
        manager = MigrationManager(temp_db)
        register_all_migrations(manager)

        # Apply first two migrations
        manager.migrate_to_latest()

        # Rollback migration 2
        manager.rollback_to_version(1)

        # Verify subscriptions table removed
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='subscriptions'")
            assert cursor.fetchone() is None

    def test_migration_3_adds_full_text_search(self, temp_db):
        """Test migration 3 adds FTS table."""
        manager = MigrationManager(temp_db)
        register_all_migrations(manager)

        # Apply all migrations
        manager.migrate_to_latest()

        # Verify FTS table exists
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='services_fts'")
            assert cursor.fetchone() is not None

    def test_all_migrations_apply_successfully(self, temp_db):
        """Test all registered migrations apply without errors."""
        manager = MigrationManager(temp_db)
        register_all_migrations(manager)

        success = manager.migrate_to_latest()
        assert success is True

        # Verify we're at latest version
        expected_version = max(m.version for m in manager.migrations)
        assert manager.get_current_version() == expected_version


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
