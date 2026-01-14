"""
Database Connection Pool

Provides connection pooling for SQLite database to improve performance
and manage connections efficiently.
"""

import sqlite3
import logging
import threading
from queue import Queue, Empty
from contextlib import contextmanager
from typing import Optional
from pathlib import Path

logger = logging.getLogger('dms.connection_pool')


class ConnectionPool:
    """
    Connection pool for SQLite database.

    Manages a pool of reusable database connections to improve performance
    and prevent connection exhaustion.
    """

    def __init__(self, db_path: str, pool_size: int = 5, timeout: int = 30):
        """
        Initialize connection pool.

        Args:
            db_path: Path to database file
            pool_size: Maximum number of connections in pool
            timeout: Timeout for getting connection from pool (seconds)
        """
        self.db_path = db_path
        self.pool_size = pool_size
        self.timeout = timeout
        self._pool: Queue = Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        self._connections_created = 0

        logger.info(f"Initializing connection pool (size: {pool_size}, timeout: {timeout}s)")

        # Pre-create connections
        self._initialize_pool()

    def _initialize_pool(self):
        """Pre-create connections for the pool."""
        with self._lock:
            for i in range(self.pool_size):
                try:
                    conn = self._create_connection()
                    self._pool.put(conn, block=False)
                    logger.debug(f"Created connection {i+1}/{self.pool_size}")
                except Exception as e:
                    logger.error(f"Failed to create connection {i+1}: {e}")
                    break

    def _create_connection(self) -> sqlite3.Connection:
        """
        Create a new database connection.

        Returns:
            SQLite connection object
        """
        # Ensure database directory exists
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        # Create connection with optimizations
        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,  # Allow connection to be used across threads
            timeout=self.timeout
        )

        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")

        # Performance optimizations
        conn.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging
        conn.execute("PRAGMA synchronous = NORMAL")  # Balance safety and speed
        conn.execute("PRAGMA temp_store = MEMORY")  # Store temp tables in memory
        conn.execute("PRAGMA mmap_size = 30000000000")  # Memory-mapped I/O
        conn.execute("PRAGMA page_size = 4096")  # Optimal page size

        # Set row factory for dict-like access
        conn.row_factory = sqlite3.Row

        with self._lock:
            self._connections_created += 1

        logger.debug(f"Created new connection (total: {self._connections_created})")
        return conn

    def get_connection(self) -> sqlite3.Connection:
        """
        Get a connection from the pool.

        Returns:
            Database connection

        Raises:
            TimeoutError: If no connection available within timeout
        """
        try:
            # Try to get existing connection from pool
            conn = self._pool.get(block=True, timeout=self.timeout)

            # Verify connection is still valid
            try:
                conn.execute("SELECT 1")
                logger.debug("Retrieved connection from pool")
                return conn
            except sqlite3.Error:
                # Connection is invalid, create new one
                logger.warning("Connection invalid, creating new one")
                return self._create_connection()

        except Empty:
            # No connections available, create new one if under limit
            with self._lock:
                if self._connections_created < self.pool_size * 2:
                    logger.warning("Pool exhausted, creating additional connection")
                    return self._create_connection()
                else:
                    raise TimeoutError(
                        f"Could not get database connection within {self.timeout}s. "
                        f"Pool exhausted ({self._connections_created} connections created)."
                    )

    def return_connection(self, conn: sqlite3.Connection):
        """
        Return a connection to the pool.

        Args:
            conn: Connection to return
        """
        try:
            # Rollback any uncommitted transactions
            if conn.in_transaction:
                conn.rollback()

            # Try to return to pool
            try:
                self._pool.put(conn, block=False)
                logger.debug("Returned connection to pool")
            except:
                # Pool is full, close connection
                conn.close()
                logger.debug("Pool full, closed connection")

        except Exception as e:
            logger.error(f"Error returning connection to pool: {e}")
            try:
                conn.close()
            except:
                pass

    @contextmanager
    def get_connection_context(self):
        """
        Context manager for getting and returning connections.

        Example:
            with pool.get_connection_context() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM services")
        """
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()  # Auto-commit on success
        except Exception:
            conn.rollback()  # Auto-rollback on error
            raise
        finally:
            self.return_connection(conn)

    def close_all(self):
        """Close all connections in the pool."""
        logger.info("Closing all connections in pool")
        closed = 0

        while not self._pool.empty():
            try:
                conn = self._pool.get(block=False)
                conn.close()
                closed += 1
            except (Empty, Exception) as e:
                logger.debug(f"Error closing connection: {e}")
                break

        logger.info(f"Closed {closed} connections")

    def get_stats(self) -> dict:
        """
        Get pool statistics.

        Returns:
            Dictionary with pool stats
        """
        return {
            'pool_size': self.pool_size,
            'connections_created': self._connections_created,
            'available_connections': self._pool.qsize(),
            'active_connections': self._connections_created - self._pool.qsize()
        }

    def __enter__(self):
        """Support context manager protocol."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close pool when exiting context."""
        self.close_all()


# Singleton instance
_pool_instance: Optional[ConnectionPool] = None
_pool_lock = threading.Lock()


def get_connection_pool(db_path: str = None, pool_size: int = 5) -> ConnectionPool:
    """
    Get singleton connection pool instance.

    Args:
        db_path: Path to database (only used on first call)
        pool_size: Pool size (only used on first call)

    Returns:
        ConnectionPool instance
    """
    global _pool_instance

    if _pool_instance is None:
        with _pool_lock:
            if _pool_instance is None:
                if db_path is None:
                    raise ValueError("db_path required for first pool initialization")
                _pool_instance = ConnectionPool(db_path, pool_size)
                logger.info("Created singleton connection pool")

    return _pool_instance


def close_connection_pool():
    """Close singleton connection pool."""
    global _pool_instance

    if _pool_instance is not None:
        with _pool_lock:
            if _pool_instance is not None:
                _pool_instance.close_all()
                _pool_instance = None
                logger.info("Closed singleton connection pool")
