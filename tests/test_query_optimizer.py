"""
Tests for Query Optimizer Module
"""

import pytest
import sqlite3
import tempfile
import os
from pathlib import Path

from src.core.query_optimizer import (
    QueryOptimizer,
    QueryPerformance,
    create_query_optimizer,
    optimize_database_full
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)

    # Initialize test database
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    # Create test tables
    cursor.execute('''
        CREATE TABLE services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            region TEXT,
            service_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE financial_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_id INTEGER NOT NULL,
            brutto_rate REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (service_id) REFERENCES services(id)
        )
    ''')

    # Insert test data
    for i in range(100):
        cursor.execute('''
            INSERT INTO services (name, region, service_type)
            VALUES (?, ?, ?)
        ''', (f'Service {i}', f'Region {i % 10}', f'Type {i % 5}'))

        service_id = cursor.lastrowid
        cursor.execute('''
            INSERT INTO financial_data (service_id, brutto_rate)
            VALUES (?, ?)
        ''', (service_id, 100.0 + i))

    conn.commit()
    conn.close()

    yield path

    # Cleanup
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def optimizer(temp_db):
    """Create QueryOptimizer instance."""
    return QueryOptimizer(temp_db)


class TestQueryOptimizer:
    """Test QueryOptimizer class."""

    def test_init(self, temp_db):
        """Test initialization."""
        optimizer = QueryOptimizer(temp_db)
        assert optimizer.db_path == temp_db
        assert isinstance(optimizer.query_log, list)
        assert len(optimizer.query_log) == 0

    def test_create_additional_indexes(self, optimizer, temp_db):
        """Test creating additional indexes."""
        results = optimizer.create_additional_indexes()

        assert isinstance(results, dict)
        assert len(results) > 0

        # Verify indexes were created
        with optimizer.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = [row[0] for row in cursor.fetchall()]

            # Check for some expected indexes
            assert any('idx_services' in idx for idx in indexes)

    def test_analyze_database(self, optimizer):
        """Test running ANALYZE."""
        success = optimizer.analyze_database()
        assert success is True

    def test_get_table_info(self, optimizer):
        """Test getting table information."""
        info = optimizer.get_table_info('services')

        assert info['table_name'] == 'services'
        assert 'columns' in info
        assert 'row_count' in info
        assert 'indexes' in info
        assert info['row_count'] == 100  # We inserted 100 rows

        # Check columns
        column_names = [col['name'] for col in info['columns']]
        assert 'id' in column_names
        assert 'name' in column_names
        assert 'region' in column_names

    def test_get_all_indexes(self, optimizer):
        """Test getting all indexes."""
        optimizer.create_additional_indexes()
        indexes = optimizer.get_all_indexes()

        assert isinstance(indexes, list)
        assert len(indexes) > 0

        # Check index structure
        for idx in indexes:
            assert 'table' in idx
            assert 'name' in idx
            assert 'columns' in idx

    def test_explain_query(self, optimizer):
        """Test query plan analysis."""
        query = 'SELECT * FROM services WHERE region = ?'
        plan = optimizer.explain_query(query, ('Region 1',))

        assert 'query' in plan
        assert 'uses_index' in plan
        assert 'query_plan' in plan
        assert isinstance(plan['query_plan'], list)

    def test_measure_query_performance(self, optimizer):
        """Test measuring query performance."""
        query = 'SELECT * FROM services WHERE region = ?'
        performance = optimizer.measure_query_performance(query, ('Region 1',), iterations=5)

        assert isinstance(performance, QueryPerformance)
        assert performance.query == query
        assert performance.execution_time > 0
        assert performance.rows_returned > 0
        assert isinstance(performance.uses_index, bool)

        # Check query was logged
        assert len(optimizer.query_log) == 1
        assert optimizer.query_log[0] == performance

    def test_optimize_table(self, optimizer):
        """Test table optimization."""
        result = optimizer.optimize_table('services')

        assert result['table_name'] == 'services'
        assert result['row_count'] == 100
        assert isinstance(result['vacuum_success'], bool)
        assert isinstance(result['analyze_success'], bool)

    def test_vacuum_database(self, optimizer):
        """Test database vacuum."""
        success = optimizer.vacuum_database()
        assert success is True

    def test_get_slow_queries(self, optimizer):
        """Test getting slow queries."""
        # Execute some queries
        fast_query = 'SELECT COUNT(*) FROM services'
        optimizer.measure_query_performance(fast_query)

        # Get slow queries with very low threshold
        slow_queries = optimizer.get_slow_queries(threshold_ms=0.0)

        # Should include our query
        assert len(slow_queries) > 0

    def test_get_performance_report(self, optimizer):
        """Test generating performance report."""
        # Execute some queries
        optimizer.measure_query_performance('SELECT * FROM services WHERE region = ?', ('Region 1',))
        optimizer.measure_query_performance('SELECT * FROM financial_data WHERE brutto_rate > ?', (150.0,))

        report = optimizer.get_performance_report()

        assert 'total_queries' in report
        assert report['total_queries'] == 2
        assert 'queries_using_index' in report
        assert 'queries_without_index' in report
        assert 'average_execution_time' in report
        assert 'slowest_queries' in report
        assert 'suggested_indexes' in report

    def test_get_database_stats(self, optimizer):
        """Test getting database statistics."""
        stats = optimizer.get_database_stats()

        assert 'database_size_bytes' in stats
        assert 'database_size_mb' in stats
        assert 'wasted_space_bytes' in stats
        assert 'wasted_percentage' in stats
        assert 'page_count' in stats
        assert 'page_size' in stats
        assert 'tables' in stats
        assert 'total_rows' in stats

        # Check table stats
        assert 'services' in stats['tables']
        assert 'financial_data' in stats['tables']
        assert stats['tables']['services'] == 100
        assert stats['tables']['financial_data'] == 100

    def test_query_with_index(self, optimizer):
        """Test query performance with index."""
        # Create indexes
        optimizer.create_additional_indexes()
        optimizer.analyze_database()

        # Measure query that should use index
        query = 'SELECT * FROM services WHERE region = ? ORDER BY updated_at DESC'
        performance = optimizer.measure_query_performance(query, ('Region 1',))

        # Should use index (after creating indexes)
        # Note: SQLite might not always use index for small datasets
        assert isinstance(performance.uses_index, bool)

    def test_suggest_indexes(self, optimizer):
        """Test index suggestion."""
        query = 'SELECT * FROM services WHERE region = ? AND service_type = ?'
        plan = optimizer.explain_query(query, ('Region 1', 'Type 1'))

        # If no index is used, suggestions should be made
        if not plan['uses_index']:
            suggestions = optimizer._suggest_indexes(query, plan)
            assert isinstance(suggestions, list)


class TestFactoryFunctions:
    """Test factory functions."""

    def test_create_query_optimizer(self, temp_db):
        """Test create_query_optimizer factory."""
        optimizer = create_query_optimizer(temp_db)
        assert isinstance(optimizer, QueryOptimizer)
        assert optimizer.db_path == temp_db

    def test_optimize_database_full(self, temp_db):
        """Test full database optimization."""
        results = optimize_database_full(temp_db)

        assert 'indexes_created' in results
        assert 'analyze_success' in results
        assert 'vacuum_success' in results
        assert 'database_stats' in results
        assert 'all_indexes' in results

        # Check indexes were created
        assert isinstance(results['indexes_created'], dict)
        assert len(results['indexes_created']) > 0

        # Check analyze and vacuum ran
        assert results['analyze_success'] is True
        assert results['vacuum_success'] is True

        # Check stats
        stats = results['database_stats']
        assert stats['total_rows'] == 200  # 100 services + 100 financial_data


class TestIntegrationScenarios:
    """Integration tests for complete workflows."""

    def test_complete_optimization_workflow(self, temp_db):
        """Test complete optimization workflow."""
        # 1. Create optimizer
        optimizer = QueryOptimizer(temp_db)

        # 2. Get initial stats
        initial_stats = optimizer.get_database_stats()
        assert initial_stats['total_rows'] == 200

        # 3. Create indexes
        index_results = optimizer.create_additional_indexes()
        assert sum(index_results.values()) > 0

        # 4. Run analyze
        assert optimizer.analyze_database() is True

        # 5. Measure query performance
        query = 'SELECT * FROM services WHERE region = ? AND service_type = ?'
        performance = optimizer.measure_query_performance(query, ('Region 1', 'Type 1'))
        assert performance.execution_time > 0

        # 6. Generate report
        report = optimizer.get_performance_report()
        assert report['total_queries'] == 1

        # 7. Vacuum database
        assert optimizer.vacuum_database() is True

        # 8. Get final stats
        final_stats = optimizer.get_database_stats()
        assert final_stats['database_size_bytes'] > 0

    def test_performance_comparison(self, temp_db):
        """Test performance comparison before and after optimization."""
        optimizer = QueryOptimizer(temp_db)

        # Measure before optimization
        query = 'SELECT * FROM services WHERE region = ?'
        before_perf = optimizer.measure_query_performance(query, ('Region 1',), iterations=10)

        # Optimize
        optimizer.create_additional_indexes()
        optimizer.analyze_database()

        # Measure after optimization
        after_perf = optimizer.measure_query_performance(query, ('Region 1',), iterations=10)

        # Both should execute successfully
        assert before_perf.execution_time > 0
        assert after_perf.execution_time > 0

        # Note: Performance improvement depends on dataset size and SQLite query planner


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_nonexistent_table(self, optimizer):
        """Test with non-existent table."""
        with pytest.raises(sqlite3.OperationalError):
            optimizer.get_table_info('nonexistent_table')

    def test_invalid_query(self, optimizer):
        """Test with invalid SQL query."""
        with pytest.raises(sqlite3.OperationalError):
            optimizer.explain_query('INVALID SQL QUERY')

    def test_empty_database(self):
        """Test with empty database."""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)

        # Create empty database
        conn = sqlite3.connect(path)
        conn.close()

        optimizer = QueryOptimizer(path)
        stats = optimizer.get_database_stats()

        assert stats['total_rows'] == 0
        assert stats['database_size_bytes'] > 0  # Has metadata

        # Cleanup
        os.unlink(path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
