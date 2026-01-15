"""
Query Optimization and Database Performance Module

Provides query analysis, index management, and performance optimization
for SQLite database operations.
"""

import sqlite3
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger('dms.query_optimizer')


@dataclass
class QueryPerformance:
    """Query performance metrics."""
    query: str
    execution_time: float
    rows_examined: int
    rows_returned: int
    uses_index: bool
    suggested_indexes: List[str]
    timestamp: datetime


class QueryOptimizer:
    """Optimize database queries and manage indexes."""

    def __init__(self, db_path: str):
        """
        Initialize query optimizer.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.query_log: List[QueryPerformance] = []
        logger.info(f"Query optimizer initialized for database: {db_path}")

    @contextmanager
    def get_connection(self):
        """Get database connection context manager."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def create_additional_indexes(self) -> Dict[str, bool]:
        """
        Create additional performance indexes.

        Returns:
            Dictionary mapping index name to success status
        """
        logger.info("Creating additional performance indexes")

        indexes = {
            # Composite indexes for common query patterns
            'idx_services_type_region': 'CREATE INDEX IF NOT EXISTS idx_services_type_region ON services(service_type, region)',
            'idx_services_updated': 'CREATE INDEX IF NOT EXISTS idx_services_updated ON services(updated_at DESC)',
            'idx_services_created': 'CREATE INDEX IF NOT EXISTS idx_services_created ON services(created_at DESC)',

            # Composite index for versions
            'idx_versions_service_version': 'CREATE INDEX IF NOT EXISTS idx_versions_service_version ON versions(service_id, version_number DESC)',

            # Financial data indexes
            'idx_financial_created': 'CREATE INDEX IF NOT EXISTS idx_financial_created ON financial_data(created_at DESC)',
            'idx_financial_rate': 'CREATE INDEX IF NOT EXISTS idx_financial_rate ON financial_data(brutto_rate)',

            # Subscription composite indexes
            'idx_subscriptions_tenant_status': 'CREATE INDEX IF NOT EXISTS idx_subscriptions_tenant_status ON subscriptions(tenant_id, status)',
            'idx_subscriptions_status_created': 'CREATE INDEX IF NOT EXISTS idx_subscriptions_status_created ON subscriptions(status, created_at DESC)',

            # Covering index for common service queries
            'idx_services_name_region_type': 'CREATE INDEX IF NOT EXISTS idx_services_name_region_type ON services(name, region, service_type)',
        }

        results = {}
        with self.get_connection() as conn:
            cursor = conn.cursor()

            for index_name, create_sql in indexes.items():
                try:
                    cursor.execute(create_sql)
                    results[index_name] = True
                    logger.info(f"Created index: {index_name}")
                except sqlite3.Error as e:
                    logger.error(f"Failed to create index {index_name}: {e}")
                    results[index_name] = False

            conn.commit()

        logger.info(f"Index creation complete: {sum(results.values())}/{len(results)} successful")
        return results

    def analyze_database(self) -> bool:
        """
        Run ANALYZE to update query planner statistics.

        Returns:
            True if successful
        """
        logger.info("Running ANALYZE to update query planner statistics")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('ANALYZE')
                conn.commit()

            logger.info("ANALYZE completed successfully")
            return True

        except sqlite3.Error as e:
            logger.error(f"ANALYZE failed: {e}")
            return False

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a table.

        Args:
            table_name: Name of the table

        Returns:
            Dictionary with table information
        """
        logger.debug(f"Getting info for table: {table_name}")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get column info
            cursor.execute(f'PRAGMA table_info({table_name})')
            columns = cursor.fetchall()

            # Get row count
            cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
            row_count = cursor.fetchone()[0]

            # Get indexes
            cursor.execute(f'PRAGMA index_list({table_name})')
            indexes = cursor.fetchall()

            return {
                'table_name': table_name,
                'columns': [
                    {
                        'name': col[1],
                        'type': col[2],
                        'not_null': bool(col[3]),
                        'default': col[4],
                        'primary_key': bool(col[5])
                    }
                    for col in columns
                ],
                'row_count': row_count,
                'indexes': [
                    {
                        'name': idx[1],
                        'unique': bool(idx[2]),
                        'origin': idx[3]
                    }
                    for idx in indexes
                ]
            }

    def get_all_indexes(self) -> List[Dict[str, Any]]:
        """
        Get all indexes in the database.

        Returns:
            List of index information
        """
        logger.debug("Retrieving all database indexes")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get all tables
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            tables = [row[0] for row in cursor.fetchall()]

            all_indexes = []
            for table in tables:
                cursor.execute(f'PRAGMA index_list({table})')
                indexes = cursor.fetchall()

                for idx in indexes:
                    index_name = idx[1]

                    # Get index details
                    cursor.execute(f'PRAGMA index_info({index_name})')
                    columns = cursor.fetchall()

                    all_indexes.append({
                        'table': table,
                        'name': index_name,
                        'unique': bool(idx[2]),
                        'columns': [col[2] for col in columns]
                    })

        logger.info(f"Found {len(all_indexes)} indexes")
        return all_indexes

    def explain_query(self, query: str, params: Tuple = ()) -> Dict[str, Any]:
        """
        Analyze query execution plan.

        Args:
            query: SQL query to analyze
            params: Query parameters

        Returns:
            Dictionary with execution plan information
        """
        logger.debug(f"Analyzing query: {query[:100]}...")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get query plan
            explain_query = f'EXPLAIN QUERY PLAN {query}'
            cursor.execute(explain_query, params)
            query_plan = cursor.fetchall()

            # Check if indexes are used
            uses_index = any('USING INDEX' in str(row) for row in query_plan)

            # Get detailed plan
            cursor.execute(f'EXPLAIN {query}', params)
            detailed_plan = cursor.fetchall()

            return {
                'query': query,
                'uses_index': uses_index,
                'query_plan': [
                    {
                        'id': row[0],
                        'parent': row[1],
                        'detail': row[3]
                    }
                    for row in query_plan
                ],
                'instructions': len(detailed_plan)
            }

    def measure_query_performance(
        self,
        query: str,
        params: Tuple = (),
        iterations: int = 1
    ) -> QueryPerformance:
        """
        Measure query execution performance.

        Args:
            query: SQL query to measure
            params: Query parameters
            iterations: Number of times to execute query

        Returns:
            QueryPerformance object with metrics
        """
        logger.debug(f"Measuring query performance: {query[:100]}...")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Warm up
            cursor.execute(query, params)
            cursor.fetchall()

            # Measure execution time
            start_time = time.time()
            for _ in range(iterations):
                cursor.execute(query, params)
                results = cursor.fetchall()
            end_time = time.time()

            avg_time = (end_time - start_time) / iterations

            # Get execution plan
            plan = self.explain_query(query, params)

            # Analyze for index suggestions
            suggested_indexes = self._suggest_indexes(query, plan)

            performance = QueryPerformance(
                query=query,
                execution_time=avg_time,
                rows_examined=-1,  # SQLite doesn't easily provide this
                rows_returned=len(results),
                uses_index=plan['uses_index'],
                suggested_indexes=suggested_indexes,
                timestamp=datetime.now()
            )

            self.query_log.append(performance)
            logger.info(f"Query completed in {avg_time*1000:.2f}ms, uses_index={plan['uses_index']}")

            return performance

    def _suggest_indexes(self, query: str, plan: Dict[str, Any]) -> List[str]:
        """
        Suggest indexes based on query analysis.

        Args:
            query: SQL query
            plan: Query execution plan

        Returns:
            List of suggested index creation statements
        """
        suggestions = []

        # Check if table scan is being used
        for step in plan['query_plan']:
            detail = step['detail']

            if 'SCAN' in detail and 'USING INDEX' not in detail:
                # Extract table name
                if 'TABLE' in detail:
                    parts = detail.split()
                    if 'TABLE' in parts:
                        table_idx = parts.index('TABLE')
                        if table_idx + 1 < len(parts):
                            table_name = parts[table_idx + 1]

                            # Suggest index based on WHERE clause
                            if 'WHERE' in query.upper():
                                # Simple heuristic: suggest index on columns in WHERE
                                where_clause = query.upper().split('WHERE')[1].split('ORDER')[0]
                                for column in ['name', 'region', 'service_type', 'status', 'tenant_id']:
                                    if column.upper() in where_clause:
                                        suggestions.append(
                                            f"CREATE INDEX idx_{table_name}_{column} ON {table_name}({column})"
                                        )

        return suggestions

    def optimize_table(self, table_name: str) -> Dict[str, Any]:
        """
        Optimize a specific table.

        Args:
            table_name: Name of table to optimize

        Returns:
            Dictionary with optimization results
        """
        logger.info(f"Optimizing table: {table_name}")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get table info before optimization
            cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
            row_count = cursor.fetchone()[0]

            # Run VACUUM on the table (SQLite VACUUM is database-wide)
            try:
                cursor.execute('VACUUM')
                vacuum_success = True
            except sqlite3.Error as e:
                logger.error(f"VACUUM failed: {e}")
                vacuum_success = False

            # Run ANALYZE
            try:
                cursor.execute(f'ANALYZE {table_name}')
                analyze_success = True
            except sqlite3.Error as e:
                logger.error(f"ANALYZE failed: {e}")
                analyze_success = False

            conn.commit()

        return {
            'table_name': table_name,
            'row_count': row_count,
            'vacuum_success': vacuum_success,
            'analyze_success': analyze_success
        }

    def vacuum_database(self) -> bool:
        """
        Vacuum database to reclaim space and defragment.

        Returns:
            True if successful
        """
        logger.info("Running VACUUM on database")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Get size before vacuum
                cursor.execute('PRAGMA page_count')
                pages_before = cursor.fetchone()[0]
                cursor.execute('PRAGMA page_size')
                page_size = cursor.fetchone()[0]
                size_before = pages_before * page_size

                # Run vacuum
                cursor.execute('VACUUM')

                # Get size after vacuum
                cursor.execute('PRAGMA page_count')
                pages_after = cursor.fetchone()[0]
                size_after = pages_after * page_size

                space_saved = size_before - size_after

                logger.info(f"VACUUM completed: saved {space_saved} bytes ({space_saved/(1024*1024):.2f} MB)")
                return True

        except sqlite3.Error as e:
            logger.error(f"VACUUM failed: {e}")
            return False

    def get_slow_queries(self, threshold_ms: float = 100.0) -> List[QueryPerformance]:
        """
        Get queries slower than threshold.

        Args:
            threshold_ms: Threshold in milliseconds

        Returns:
            List of slow queries
        """
        threshold_sec = threshold_ms / 1000.0
        slow_queries = [q for q in self.query_log if q.execution_time > threshold_sec]

        logger.info(f"Found {len(slow_queries)} slow queries (>{threshold_ms}ms)")
        return slow_queries

    def get_performance_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive performance report.

        Returns:
            Dictionary with performance metrics
        """
        logger.info("Generating performance report")

        report = {
            'total_queries': len(self.query_log),
            'queries_using_index': sum(1 for q in self.query_log if q.uses_index),
            'queries_without_index': sum(1 for q in self.query_log if not q.uses_index),
            'average_execution_time': sum(q.execution_time for q in self.query_log) / len(self.query_log) if self.query_log else 0,
            'slowest_queries': sorted(self.query_log, key=lambda q: q.execution_time, reverse=True)[:10],
            'suggested_indexes': []
        }

        # Collect unique index suggestions
        all_suggestions = set()
        for query in self.query_log:
            all_suggestions.update(query.suggested_indexes)

        report['suggested_indexes'] = list(all_suggestions)

        logger.info(f"Performance report generated: {report['total_queries']} queries analyzed")
        return report

    def enable_query_logging(self) -> bool:
        """
        Enable SQLite query logging for debugging.

        Returns:
            True if successful
        """
        try:
            with self.get_connection() as conn:
                # Enable query planner debugging
                conn.set_trace_callback(lambda query: logger.debug(f"SQL: {query}"))

            logger.info("Query logging enabled")
            return True

        except Exception as e:
            logger.error(f"Failed to enable query logging: {e}")
            return False

    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive database statistics.

        Returns:
            Dictionary with database stats
        """
        logger.info("Collecting database statistics")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Database size
            cursor.execute('PRAGMA page_count')
            page_count = cursor.fetchone()[0]
            cursor.execute('PRAGMA page_size')
            page_size = cursor.fetchone()[0]
            db_size = page_count * page_size

            # Free pages
            cursor.execute('PRAGMA freelist_count')
            freelist_count = cursor.fetchone()[0]
            wasted_space = freelist_count * page_size

            # Get all tables
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            tables = [row[0] for row in cursor.fetchall()]

            # Table stats
            table_stats = {}
            for table in tables:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                row_count = cursor.fetchone()[0]
                table_stats[table] = row_count

            return {
                'database_size_bytes': db_size,
                'database_size_mb': db_size / (1024 * 1024),
                'wasted_space_bytes': wasted_space,
                'wasted_space_mb': wasted_space / (1024 * 1024),
                'wasted_percentage': (wasted_space / db_size * 100) if db_size > 0 else 0,
                'page_count': page_count,
                'page_size': page_size,
                'tables': table_stats,
                'total_rows': sum(table_stats.values())
            }


def create_query_optimizer(db_path: str) -> QueryOptimizer:
    """
    Factory function to create QueryOptimizer instance.

    Args:
        db_path: Path to database

    Returns:
        QueryOptimizer instance
    """
    return QueryOptimizer(db_path)


def optimize_database_full(db_path: str) -> Dict[str, Any]:
    """
    Perform full database optimization.

    Args:
        db_path: Path to database

    Returns:
        Dictionary with optimization results
    """
    logger.info(f"Starting full database optimization: {db_path}")

    optimizer = QueryOptimizer(db_path)

    results = {
        'indexes_created': optimizer.create_additional_indexes(),
        'analyze_success': optimizer.analyze_database(),
        'vacuum_success': optimizer.vacuum_database(),
        'database_stats': optimizer.get_database_stats(),
        'all_indexes': optimizer.get_all_indexes()
    }

    logger.info("Full database optimization complete")
    return results
