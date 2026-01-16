"""
Tests for database connection pool.
"""

import sqlite3
import tempfile
import threading
import time
from pathlib import Path

import pytest

from src.core.connection_pool import ConnectionPool, close_connection_pool, get_connection_pool


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


class TestConnectionPool:
    """Tests for ConnectionPool class."""

    def test_initialization(self, temp_db):
        """Test pool initialization."""
        pool = ConnectionPool(temp_db, pool_size=3)
        assert pool.pool_size == 3
        assert pool.db_path == temp_db
        stats = pool.get_stats()
        assert stats["pool_size"] == 3
        assert stats["connections_created"] == 3
        pool.close_all()

    def test_get_connection(self, temp_db):
        """Test getting connection from pool."""
        pool = ConnectionPool(temp_db, pool_size=2)
        conn = pool.get_connection()
        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)
        pool.return_connection(conn)
        pool.close_all()

    def test_return_connection(self, temp_db):
        """Test returning connection to pool."""
        pool = ConnectionPool(temp_db, pool_size=2)
        conn = pool.get_connection()

        stats1 = pool.get_stats()
        available_before = stats1["available_connections"]

        pool.return_connection(conn)

        stats2 = pool.get_stats()
        available_after = stats2["available_connections"]

        assert available_after == available_before + 1
        pool.close_all()

    def test_connection_context_manager(self, temp_db):
        """Test context manager for connections."""
        pool = ConnectionPool(temp_db, pool_size=2)

        with pool.get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")

        # Verify table was created and committed
        with pool.get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test'")
            result = cursor.fetchone()
            assert result is not None

        pool.close_all()

    def test_auto_commit_on_success(self, temp_db):
        """Test automatic commit on successful context exit."""
        pool = ConnectionPool(temp_db, pool_size=2)

        with pool.get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test (id INTEGER, value TEXT)")
            cursor.execute("INSERT INTO test VALUES (1, 'test')")

        # Verify data was committed
        with pool.get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM test WHERE id = 1")
            result = cursor.fetchone()
            assert result is not None
            assert result[1] == "test"

        pool.close_all()

    def test_auto_rollback_on_error(self, temp_db):
        """Test automatic rollback on error."""
        pool = ConnectionPool(temp_db, pool_size=2)

        # Create table first
        with pool.get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")

        # Try to insert invalid data
        try:
            with pool.get_connection_context() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO test VALUES (1)")
                # Cause error
                cursor.execute("INSERT INTO test VALUES (1)")  # Duplicate primary key
        except sqlite3.IntegrityError:
            pass

        # Verify rollback happened
        with pool.get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM test")
            count = cursor.fetchone()[0]
            assert count == 0  # No rows inserted due to rollback

        pool.close_all()

    def test_pool_exhaustion_creates_new_connection(self, temp_db):
        """Test pool creates additional connections when exhausted."""
        pool = ConnectionPool(temp_db, pool_size=2)

        conn1 = pool.get_connection()
        conn2 = pool.get_connection()
        conn3 = pool.get_connection()  # Should create new connection

        stats = pool.get_stats()
        assert stats["connections_created"] >= 3

        pool.return_connection(conn1)
        pool.return_connection(conn2)
        pool.return_connection(conn3)
        pool.close_all()

    def test_connection_validation(self, temp_db):
        """Test connection validation."""
        pool = ConnectionPool(temp_db, pool_size=2)
        conn = pool.get_connection()

        # Connection should be valid
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1

        pool.return_connection(conn)
        pool.close_all()

    def test_pragmas_applied(self, temp_db):
        """Test that performance PRAGMAs are applied."""
        pool = ConnectionPool(temp_db, pool_size=1)

        with pool.get_connection_context() as conn:
            cursor = conn.cursor()

            # Check journal mode
            cursor.execute("PRAGMA journal_mode")
            assert cursor.fetchone()[0] == "wal"

            # Check foreign keys
            cursor.execute("PRAGMA foreign_keys")
            assert cursor.fetchone()[0] == 1

        pool.close_all()

    def test_concurrent_access(self, temp_db):
        """Test concurrent access to pool."""
        pool = ConnectionPool(temp_db, pool_size=3)
        results = []
        errors = []

        def worker(worker_id):
            try:
                with pool.get_connection_context() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT ? as id", (worker_id,))
                    result = cursor.fetchone()[0]
                    results.append(result)
                    time.sleep(0.01)  # Simulate work
            except Exception as e:
                errors.append(e)

        # Launch multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=worker, args=(i,))
            thread.start()
            threads.append(thread)

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Verify all threads succeeded
        assert len(errors) == 0
        assert len(results) == 10
        assert sorted(results) == list(range(10))

        pool.close_all()

    def test_close_all(self, temp_db):
        """Test closing all connections."""
        pool = ConnectionPool(temp_db, pool_size=3)

        stats_before = pool.get_stats()
        assert stats_before["available_connections"] == 3

        pool.close_all()

        stats_after = pool.get_stats()
        assert stats_after["available_connections"] == 0

    def test_stats(self, temp_db):
        """Test pool statistics."""
        pool = ConnectionPool(temp_db, pool_size=3)

        stats = pool.get_stats()
        assert "pool_size" in stats
        assert "connections_created" in stats
        assert "available_connections" in stats
        assert "active_connections" in stats

        assert stats["pool_size"] == 3
        assert stats["connections_created"] == 3
        assert stats["available_connections"] == 3
        assert stats["active_connections"] == 0

        # Get a connection
        conn = pool.get_connection()
        stats2 = pool.get_stats()
        assert stats2["available_connections"] == 2
        assert stats2["active_connections"] == 1

        pool.return_connection(conn)
        pool.close_all()


class TestSingletonPool:
    """Tests for singleton pool functions."""

    def test_get_connection_pool(self, temp_db):
        """Test getting singleton pool."""
        # Close any existing pool
        close_connection_pool()

        pool1 = get_connection_pool(temp_db, pool_size=3)
        pool2 = get_connection_pool()

        assert pool1 is pool2  # Should be same instance

        close_connection_pool()

    def test_get_connection_pool_requires_path_first_time(self):
        """Test that db_path is required on first call."""
        close_connection_pool()

        with pytest.raises(ValueError) as exc:
            get_connection_pool()

        assert "db_path required" in str(exc.value)

    def test_close_connection_pool(self, temp_db):
        """Test closing singleton pool."""
        close_connection_pool()

        pool = get_connection_pool(temp_db, pool_size=2)
        assert pool is not None

        close_connection_pool()

        # Should create new pool
        pool2 = get_connection_pool(temp_db, pool_size=2)
        assert pool2 is not pool


class TestPoolContextManager:
    """Tests for pool as context manager."""

    def test_pool_context_manager(self, temp_db):
        """Test using pool as context manager."""
        with ConnectionPool(temp_db, pool_size=2) as pool:
            stats = pool.get_stats()
            assert stats["pool_size"] == 2

        # Pool should be closed after exiting context
        stats_after = pool.get_stats()
        assert stats_after["available_connections"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
