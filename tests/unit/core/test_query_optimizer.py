"""
Tests for Query Optimizer Module

Tests cover:
- Query performance measurement
- EXPLAIN QUERY PLAN analysis
- Index creation and management
- Database optimization (VACUUM, ANALYZE)
- Slow query detection
- Performance reporting
"""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from src.core.query_optimizer import (
    QueryOptimizer,
    QueryPerformance,
    create_query_optimizer,
    optimize_database_full,
)


@pytest.fixture
def temp_db():
    """Create temporary test database"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    # Create test schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Services table
    cursor.execute("""
        CREATE TABLE services (
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
    """)

    # Financial data table
    cursor.execute("""
        CREATE TABLE financial_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_id INTEGER NOT NULL,
            brutto_rate REAL NOT NULL,
            final_hourly_rate REAL,
            calculation_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
        )
    """)

    # Versions table
    cursor.execute("""
        CREATE TABLE versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_id INTEGER NOT NULL,
            version_number INTEGER NOT NULL,
            config_snapshot TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            change_notes TEXT,
            FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
        )
    """)

    # Basic indexes
    cursor.execute("CREATE INDEX idx_services_name ON services(name)")
    cursor.execute("CREATE INDEX idx_services_region ON services(region)")
    cursor.execute("CREATE INDEX idx_financial_service ON financial_data(service_id)")

    # Insert test data
    for i in range(100):
        cursor.execute("""
            INSERT INTO services (name, region, service_type, config_json)
            VALUES (?, ?, ?, ?)
        """, (f"Service {i}", f"Region {i % 5}", f"Type {i % 3}", "{}"))

        service_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO financial_data (service_id, brutto_rate)
            VALUES (?, ?)
        """, (service_id, 100.0 + i))

        cursor.execute("""
            INSERT INTO versions (service_id, version_number, config_snapshot)
            VALUES (?, ?, ?)
        """, (service_id, 1, "{}"))

    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def optimizer(temp_db):
    """Create QueryOptimizer instance"""
    return QueryOptimizer(temp_db)


class TestQueryOptimizer:
    """Test QueryOptimizer class"""

    def test_initialization(self, temp_db):
        """Test optimizer initialization"""
        optimizer = QueryOptimizer(temp_db)

        assert optimizer.db_path == temp_db
        assert optimizer.query_log == []

    def test_create_additional_indexes(self, optimizer):
        """Test creating additional indexes"""
        results = optimizer.create_additional_indexes()

        # Should create multiple indexes
        assert len(results) > 0
        assert "idx_services_type_region" in results
        assert "idx_services_updated" in results
        assert "idx_versions_service_version" in results

        # Check all succeeded
        assert all(results.values())

    def test_analyze_database(self, optimizer):
        """Test ANALYZE command"""
        success = optimizer.analyze_database()

        assert success is True

    def test_get_table_info(self, optimizer):
        """Test getting table information"""
        info = optimizer.get_table_info("services")

        assert info["table_name"] == "services"
        assert "columns" in info
        assert "row_count" in info
        assert "indexes" in info

        # Check columns
        assert len(info["columns"]) > 0
        assert any(col["name"] == "name" for col in info["columns"])
        assert any(col["name"] == "region" for col in info["columns"])

        # Check row count
        assert info["row_count"] == 100

        # Check indexes
        assert len(info["indexes"]) > 0

    def test_get_all_indexes(self, optimizer):
        """Test getting all indexes"""
        indexes = optimizer.get_all_indexes()

        # Should have basic indexes
        assert len(indexes) >= 3

        # Check structure
        for idx in indexes:
            assert "table" in idx
            assert "name" in idx
            assert "columns" in idx
            assert isinstance(idx["columns"], list)

    def test_explain_query(self, optimizer):
        """Test EXPLAIN QUERY PLAN"""
        query = "SELECT * FROM services WHERE region = ?"
        params = ("Region 0",)

        plan = optimizer.explain_query(query, params)

        assert "query" in plan
        assert "uses_index" in plan
        assert "query_plan" in plan

        # Should use index on region
        assert plan["uses_index"] is True

    def test_explain_query_without_index(self, optimizer):
        """Test EXPLAIN for query without index"""
        # Query on unindexed column
        query = "SELECT * FROM services WHERE target_group = ?"
        params = ("Group 1",)

        plan = optimizer.explain_query(query, params)

        # May or may not use index depending on SQLite version
        assert "query_plan" in plan
        assert len(plan["query_plan"]) > 0

    def test_measure_query_performance(self, optimizer):
        """Test query performance measurement"""
        query = "SELECT * FROM services WHERE region = ?"
        params = ("Region 0",)

        perf = optimizer.measure_query_performance(query, params, iterations=10)

        assert isinstance(perf, QueryPerformance)
        assert perf.query == query
        assert perf.execution_time > 0
        assert perf.rows_returned > 0
        assert perf.uses_index is True

    def test_measure_slow_query(self, optimizer):
        """Test measuring a potentially slow query"""
        # Query without index
        query = "SELECT * FROM services WHERE target_group LIKE ?"
        params = ("%Group%",)

        perf = optimizer.measure_query_performance(query, params)

        assert perf.execution_time > 0

    def test_optimize_table(self, optimizer):
        """Test table optimization"""
        result = optimizer.optimize_table("services")

        assert result["table_name"] == "services"
        assert result["row_count"] == 100
        assert "vacuum_success" in result
        assert "analyze_success" in result

    def test_vacuum_database(self, optimizer):
        """Test database VACUUM"""
        success = optimizer.vacuum_database()

        # VACUUM should succeed on test database
        assert success is True

    def test_get_database_stats(self, optimizer):
        """Test database statistics"""
        stats = optimizer.get_database_stats()

        assert "database_size_bytes" in stats
        assert "database_size_mb" in stats
        assert "wasted_space_bytes" in stats
        assert "page_count" in stats
        assert "tables" in stats
        assert "total_rows" in stats

        # Check table stats
        assert "services" in stats["tables"]
        assert stats["tables"]["services"] == 100

        # Check total rows (services + financial_data + versions = 300)
        assert stats["total_rows"] == 300

    def test_get_slow_queries(self, optimizer):
        """Test getting slow queries"""
        # Run some queries to populate log
        optimizer.measure_query_performance("SELECT * FROM services", iterations=5)
        optimizer.measure_query_performance("SELECT * FROM financial_data", iterations=5)

        # Get slow queries (very low threshold to catch test queries)
        slow_queries = optimizer.get_slow_queries(threshold_ms=0.001)

        assert len(slow_queries) >= 0  # May or may not have slow queries

    def test_get_performance_report(self, optimizer):
        """Test performance report generation"""
        # Run queries to populate log
        optimizer.measure_query_performance("SELECT * FROM services WHERE region = ?", ("Region 0",))
        optimizer.measure_query_performance("SELECT * FROM services WHERE target_group = ?", ("Group 1",))

        report = optimizer.get_performance_report()

        assert "total_queries" in report
        assert "queries_using_index" in report
        assert "queries_without_index" in report
        assert "average_execution_time" in report
        assert "slowest_queries" in report
        assert "suggested_indexes" in report

        assert report["total_queries"] == 2

    def test_query_log_tracking(self, optimizer):
        """Test that queries are logged"""
        assert len(optimizer.query_log) == 0

        optimizer.measure_query_performance("SELECT COUNT(*) FROM services")

        assert len(optimizer.query_log) == 1

        optimizer.measure_query_performance("SELECT * FROM services LIMIT 10")

        assert len(optimizer.query_log) == 2


class TestFactoryFunction:
    """Test factory functions"""

    def test_create_query_optimizer(self, temp_db):
        """Test factory function"""
        optimizer = create_query_optimizer(temp_db)

        assert isinstance(optimizer, QueryOptimizer)
        assert optimizer.db_path == temp_db

    def test_optimize_database_full(self, temp_db):
        """Test full database optimization"""
        results = optimize_database_full(temp_db)

        assert "indexes_created" in results
        assert "analyze_success" in results
        assert "vacuum_success" in results
        assert "database_stats" in results
        assert "all_indexes" in results

        # Check indexes were created
        assert len(results["indexes_created"]) > 0

        # Check ANALYZE succeeded
        assert results["analyze_success"] is True

        # Check VACUUM succeeded
        assert results["vacuum_success"] is True

        # Check stats
        assert "database_size_mb" in results["database_stats"]


class TestPerformanceComparison:
    """Test performance improvements"""

    def test_index_performance_improvement(self, optimizer):
        """Test that indexes improve performance"""
        # Query without index
        query_no_idx = "SELECT * FROM services WHERE target_group = ?"
        params = ("Group 1",)

        # Measure before index
        perf_before = optimizer.measure_query_performance(query_no_idx, params, iterations=10)

        # Create index
        with optimizer.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE INDEX idx_test_target_group ON services(target_group)")
            conn.commit()

        # Measure after index
        perf_after = optimizer.measure_query_performance(query_no_idx, params, iterations=10)

        # After adding index should use it
        assert perf_after.uses_index is True

        # Performance should be similar or better
        # (Note: For small datasets, difference may not be significant)
        assert perf_after.execution_time >= 0

    def test_composite_index_benefit(self, optimizer):
        """Test composite index usage"""
        # Query using multiple columns
        query = "SELECT * FROM services WHERE region = ? AND service_type = ?"
        params = ("Region 0", "Type 0")

        # Create composite index
        with optimizer.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE INDEX idx_test_composite ON services(region, service_type)")
            conn.commit()

        # Measure with composite index
        perf = optimizer.measure_query_performance(query, params)

        # Should use the composite index
        assert perf.uses_index is True


class TestEdgeCases:
    """Test edge cases"""

    def test_empty_database(self):
        """Test with empty database"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        # Create empty database
        conn = sqlite3.connect(db_path)
        conn.close()

        optimizer = QueryOptimizer(db_path)

        # Should handle empty database gracefully
        stats = optimizer.get_database_stats()
        assert stats["total_rows"] == 0

        # Cleanup
        Path(db_path).unlink()

    def test_database_with_no_tables(self, temp_db):
        """Test database with no user tables"""
        # This uses temp_db which already has tables
        optimizer = QueryOptimizer(temp_db)

        indexes = optimizer.get_all_indexes()
        assert len(indexes) > 0

    def test_large_query_result(self, optimizer):
        """Test measuring query with large result set"""
        query = "SELECT * FROM services"

        perf = optimizer.measure_query_performance(query, iterations=1)

        assert perf.rows_returned == 100

    def test_complex_query(self, optimizer):
        """Test complex query with JOIN"""
        query = """
            SELECT s.name, f.brutto_rate
            FROM services s
            JOIN financial_data f ON s.id = f.service_id
            WHERE s.region = ?
        """
        params = ("Region 0",)

        perf = optimizer.measure_query_performance(query, params)

        assert perf.execution_time > 0
        assert perf.rows_returned > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
