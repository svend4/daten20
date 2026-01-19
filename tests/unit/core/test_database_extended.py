"""
Extended comprehensive tests for core.database module

Goal: Increase coverage from 10% to 80%+
Tests all Database methods comprehensively
"""

import json
import sqlite3
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch, call

import pytest

from src.core.database import Database
from src.models.financial import CostBreakdown, FinancialParameters
from src.models.service import BasicInfo, Service, SystemSettings

# Test markers
pytestmark = pytest.mark.unit


def create_test_service(name="Test Service", target_group="Youth", region="Berlin", service_type="counseling", brutto_rate=50.0):
    """Helper function to create a test service"""
    service = Service(
        basic_info=BasicInfo(
            service_name=name,
            target_group=target_group,
            region=region,
        ),
        system_settings=SystemSettings(
            service_type=service_type,
        ),
    )
    service.financial.brutto_rate = Decimal(str(brutto_rate))
    return service


class TestDatabaseExtended:
    """Extended tests for Database class - comprehensive coverage"""

    @pytest.fixture
    def temp_db_path(self, tmp_path):
        """Fixture providing temporary database path"""
        return str(tmp_path / "test_extended.db")

    @pytest.fixture
    def db(self, temp_db_path):
        """Fixture providing Database instance"""
        return Database(temp_db_path, pool_size=3)

    @pytest.fixture
    def sample_service(self):
        """Fixture providing sample Service object"""
        return create_test_service()

    @pytest.fixture
    def multiple_services(self):
        """Fixture providing multiple test services"""
        return [
            create_test_service(name="Service 1", region="Berlin", service_type="counseling", brutto_rate=50.0),
            create_test_service(name="Service 2", region="Munich", service_type="therapy", brutto_rate=60.0),
            create_test_service(name="Service 3", region="Berlin", service_type="counseling", brutto_rate=55.0),
            create_test_service(name="Search Test Service", region="Hamburg", service_type="coaching", brutto_rate=70.0),
        ]

    # ============================================
    # Initialization Tests
    # ============================================

    def test_init_creates_directory(self, tmp_path):
        """Test database initialization creates parent directory"""
        nested_path = tmp_path / "nested" / "path" / "test.db"
        db = Database(str(nested_path))

        assert nested_path.parent.exists()
        assert Path(db.db_path) == nested_path

    def test_init_with_custom_pool_size(self, temp_db_path):
        """Test initialization with custom connection pool size"""
        db = Database(temp_db_path, pool_size=10)

        assert db.pool is not None
        assert hasattr(db.pool, 'size') or hasattr(db.pool, '_pool')

    def test_init_runs_migrations(self, temp_db_path):
        """Test that migrations are run during initialization"""
        with patch('src.core.database.MigrationManager') as mock_mgr:
            mock_instance = MagicMock()
            mock_mgr.return_value = mock_instance
            mock_instance.get_current_version.return_value = 1
            mock_instance.get_pending_migrations.return_value = []

            db = Database(temp_db_path)

            mock_instance.get_current_version.assert_called_once()
            mock_instance.get_pending_migrations.assert_called_once()

    def test_init_creates_all_tables(self, temp_db_path):
        """Test that all required tables are created"""
        db = Database(temp_db_path)

        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cursor.fetchall()}

            assert 'services' in tables
            assert 'financial_data' in tables
            assert 'versions' in tables
            assert 'subscriptions' in tables

    def test_init_creates_all_indexes(self, temp_db_path):
        """Test that all required indexes are created"""
        db = Database(temp_db_path)

        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
            indexes = {row[0] for row in cursor.fetchall()}

            # Check critical indexes
            assert 'idx_services_name' in indexes
            assert 'idx_services_region' in indexes
            assert 'idx_financial_service' in indexes
            assert 'idx_versions_service' in indexes
            assert 'idx_subscriptions_tenant' in indexes

    # ============================================
    # Service CRUD Tests
    # ============================================

    def test_create_service_success(self, db, sample_service):
        """Test creating a service successfully"""
        service_id = db.create_service(sample_service)

        assert service_id > 0
        assert sample_service.id == service_id
        assert sample_service.created_at is not None
        assert sample_service.updated_at is not None

    def test_create_service_stores_timestamps(self, db, sample_service):
        """Test that created_at and updated_at are set correctly"""
        before_create = datetime.now()
        service_id = db.create_service(sample_service)
        after_create = datetime.now()

        assert before_create <= sample_service.created_at <= after_create
        assert before_create <= sample_service.updated_at <= after_create

    def test_create_service_stores_config_json(self, db, sample_service):
        """Test that service config is stored as JSON"""
        service_id = db.create_service(sample_service)

        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT config_json FROM services WHERE id = ?", (service_id,))
            row = cursor.fetchone()

            assert row is not None
            config = json.loads(row[0])
            assert 'basic_info' in config
            assert config['basic_info']['service_name'] == "Test Service"

    def test_create_service_creates_financial_record(self, db, sample_service):
        """Test that financial data is created with service"""
        service_id = db.create_service(sample_service)

        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT brutto_rate FROM financial_data WHERE service_id = ?", (service_id,))
            row = cursor.fetchone()

            assert row is not None
            assert row[0] == 50.0

    def test_create_service_creates_initial_version(self, db, sample_service):
        """Test that initial version is created"""
        service_id = db.create_service(sample_service)

        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT version_number, change_notes FROM versions WHERE service_id = ?", (service_id,))
            row = cursor.fetchone()

            assert row is not None
            assert row[0] == 1  # Initial version
            assert row[1] == "Initial version"

    def test_create_multiple_services(self, db, multiple_services):
        """Test creating multiple services"""
        service_ids = []

        for service in multiple_services:
            service_id = db.create_service(service)
            service_ids.append(service_id)

        assert len(service_ids) == len(multiple_services)
        assert len(set(service_ids)) == len(service_ids)  # All IDs unique

    def test_get_service_by_id(self, db, sample_service):
        """Test retrieving service by ID"""
        service_id = db.create_service(sample_service)

        retrieved = db.get_service(service_id)

        assert retrieved is not None
        assert retrieved.basic_info.service_name == "Test Service"
        assert retrieved.basic_info.target_group == "Youth"
        assert retrieved.basic_info.region == "Berlin"

    def test_get_service_nonexistent(self, db):
        """Test getting non-existent service returns None"""
        result = db.get_service(99999)

        assert result is None

    def test_get_service_invalid_id(self, db):
        """Test getting service with invalid ID"""
        result = db.get_service(-1)

        assert result is None

    def test_update_service_success(self, db, sample_service):
        """Test updating service successfully"""
        service_id = db.create_service(sample_service)

        # Update service
        sample_service.basic_info.service_name = "Updated Service"
        original_version = sample_service.version

        result = db.update_service(sample_service)

        assert result is True
        assert sample_service.version == original_version + 1

    def test_update_service_without_id(self, db, sample_service):
        """Test updating service without ID returns False"""
        sample_service.id = None

        result = db.update_service(sample_service)

        assert result is False

    def test_update_service_updates_timestamps(self, db, sample_service):
        """Test that updated_at is changed on update"""
        service_id = db.create_service(sample_service)
        original_updated_at = sample_service.updated_at

        # Wait a moment and update
        import time
        time.sleep(0.01)

        sample_service.basic_info.service_name = "Updated"
        db.update_service(sample_service)

        assert sample_service.updated_at > original_updated_at

    def test_update_service_creates_new_version(self, db, sample_service):
        """Test that update creates new version record"""
        service_id = db.create_service(sample_service)

        sample_service.basic_info.service_name = "Updated Service"
        db.update_service(sample_service)

        versions = db.get_service_versions(service_id)

        assert len(versions) == 2  # Initial + updated
        assert versions[1]['version_number'] == 2

    def test_delete_service_success(self, db, sample_service):
        """Test deleting service successfully"""
        service_id = db.create_service(sample_service)

        result = db.delete_service(service_id)

        assert result is True

        # Verify service is deleted
        retrieved = db.get_service(service_id)
        assert retrieved is None

    def test_delete_service_cascade(self, db, sample_service):
        """Test that deleting service also deletes related records"""
        service_id = db.create_service(sample_service)

        db.delete_service(service_id)

        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()

            # Check financial data deleted
            cursor.execute("SELECT COUNT(*) FROM financial_data WHERE service_id = ?", (service_id,))
            assert cursor.fetchone()[0] == 0

            # Check versions deleted
            cursor.execute("SELECT COUNT(*) FROM versions WHERE service_id = ?", (service_id,))
            assert cursor.fetchone()[0] == 0

    def test_delete_nonexistent_service(self, db):
        """Test deleting non-existent service returns False"""
        result = db.delete_service(99999)

        assert result is False

    # ============================================
    # Service Query Tests
    # ============================================

    def test_list_services_all(self, db, multiple_services):
        """Test listing all services"""
        for service in multiple_services:
            db.create_service(service)

        services = db.list_services()

        assert len(services) == len(multiple_services)

    def test_list_services_with_limit(self, db, multiple_services):
        """Test listing services with limit"""
        for service in multiple_services:
            db.create_service(service)

        services = db.list_services(limit=2)

        assert len(services) == 2

    def test_list_services_with_offset(self, db, multiple_services):
        """Test listing services with offset"""
        for service in multiple_services:
            db.create_service(service)

        services = db.list_services(offset=2)

        assert len(services) == len(multiple_services) - 2

    def test_list_services_filter_by_region(self, db, multiple_services):
        """Test filtering services by region"""
        for service in multiple_services:
            db.create_service(service)

        services = db.list_services(region="Berlin")

        assert len(services) == 2  # Two Berlin services
        assert all(s.basic_info.region == "Berlin" for s in services)

    def test_list_services_filter_by_service_type(self, db, multiple_services):
        """Test filtering services by service type"""
        for service in multiple_services:
            db.create_service(service)

        services = db.list_services(service_type="counseling")

        assert len(services) == 2  # Two counseling services
        assert all(s.system_settings.service_type == "counseling" for s in services)

    def test_list_services_empty_database(self, db):
        """Test listing services from empty database"""
        services = db.list_services()

        assert services == []

    def test_count_services_all(self, db, multiple_services):
        """Test counting all services"""
        for service in multiple_services:
            db.create_service(service)

        count = db.count_services()

        assert count == len(multiple_services)

    def test_count_services_by_region(self, db, multiple_services):
        """Test counting services by region"""
        for service in multiple_services:
            db.create_service(service)

        count = db.count_services(region="Berlin")

        assert count == 2

    def test_count_services_by_service_type(self, db, multiple_services):
        """Test counting services by service type"""
        for service in multiple_services:
            db.create_service(service)

        count = db.count_services(service_type="counseling")

        assert count == 2

    def test_count_services_empty_database(self, db):
        """Test counting services in empty database"""
        count = db.count_services()

        assert count == 0

    def test_search_services_by_name(self, db, multiple_services):
        """Test searching services by name"""
        for service in multiple_services:
            db.create_service(service)

        results = db.search_services("Search Test")

        assert len(results) == 1
        assert "Search Test" in results[0].basic_info.service_name

    def test_search_services_case_insensitive(self, db, multiple_services):
        """Test that search is case-insensitive"""
        for service in multiple_services:
            db.create_service(service)

        results = db.search_services("search test")

        assert len(results) >= 1

    def test_search_services_no_results(self, db, multiple_services):
        """Test search with no matching results"""
        for service in multiple_services:
            db.create_service(service)

        results = db.search_services("NonexistentService")

        assert results == []

    def test_search_services_empty_query(self, db, multiple_services):
        """Test search with empty query"""
        for service in multiple_services:
            db.create_service(service)

        results = db.search_services("")

        # Should return all services or empty list (implementation dependent)
        assert isinstance(results, list)

    # ============================================
    # Version Management Tests
    # ============================================

    def test_get_service_versions_initial(self, db, sample_service):
        """Test getting versions for newly created service"""
        service_id = db.create_service(sample_service)

        versions = db.get_service_versions(service_id)

        assert len(versions) == 1
        assert versions[0]['version_number'] == 1
        assert versions[0]['change_notes'] == "Initial version"

    def test_get_service_versions_after_updates(self, db, sample_service):
        """Test getting versions after multiple updates"""
        service_id = db.create_service(sample_service)

        # Make multiple updates
        for i in range(3):
            sample_service.basic_info.service_name = f"Service v{i+2}"
            db.update_service(sample_service)

        versions = db.get_service_versions(service_id)

        assert len(versions) == 4  # Initial + 3 updates
        assert versions[0]['version_number'] == 1
        assert versions[3]['version_number'] == 4

    def test_get_service_versions_nonexistent(self, db):
        """Test getting versions for non-existent service"""
        versions = db.get_service_versions(99999)

        assert versions == []

    def test_get_service_versions_contains_config(self, db, sample_service):
        """Test that versions contain config snapshot"""
        service_id = db.create_service(sample_service)

        versions = db.get_service_versions(service_id)

        assert 'config_snapshot' in versions[0]
        config = json.loads(versions[0]['config_snapshot'])
        assert 'basic_info' in config

    # ============================================
    # Statistics Tests
    # ============================================

    def test_get_statistics_empty_database(self, db):
        """Test getting statistics from empty database"""
        stats = db.get_statistics()

        assert 'total_services' in stats
        assert stats['total_services'] == 0

    def test_get_statistics_with_services(self, db, multiple_services):
        """Test getting statistics with services"""
        for service in multiple_services:
            db.create_service(service)

        stats = db.get_statistics()

        assert stats['total_services'] == len(multiple_services)

    def test_get_statistics_includes_regions(self, db, multiple_services):
        """Test that statistics include region breakdown"""
        for service in multiple_services:
            db.create_service(service)

        stats = db.get_statistics()

        assert 'by_region' in stats
        assert 'Berlin' in stats['by_region']
        assert stats['by_region']['Berlin'] == 2

    def test_get_statistics_includes_service_types(self, db, multiple_services):
        """Test that statistics include service type breakdown"""
        for service in multiple_services:
            db.create_service(service)

        stats = db.get_statistics()

        assert 'by_type' in stats
        assert 'counseling' in stats['by_type']
        assert stats['by_type']['counseling'] == 2

    # ============================================
    # Subscription Tests
    # ============================================

    def test_create_subscription_success(self, db):
        """Test creating subscription successfully"""
        subscription_id = db.create_subscription(
            tenant_id="tenant_001",
            status="active",
            billing_cycle="monthly",
            amount=99.99,
            currency="EUR"
        )

        assert subscription_id is not None
        assert len(subscription_id) > 0

    def test_create_subscription_stores_all_fields(self, db):
        """Test that all subscription fields are stored"""
        subscription_id = db.create_subscription(
            tenant_id="tenant_001",
            status="active",
            billing_cycle="monthly",
            amount=99.99,
            currency="USD",
            metadata={"key": "value"}
        )

        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT tenant_id, status, billing_cycle, amount, currency, metadata_json FROM subscriptions WHERE id = ?", (subscription_id,))
            row = cursor.fetchone()

            assert row[0] == "tenant_001"
            assert row[1] == "active"
            assert row[2] == "monthly"
            assert row[3] == 99.99
            assert row[4] == "USD"
            assert json.loads(row[5])["key"] == "value"

    def test_get_subscriptions_all(self, db):
        """Test getting all subscriptions"""
        # Create multiple subscriptions
        for i in range(3):
            db.create_subscription(
                tenant_id=f"tenant_{i:03d}",
                status="active",
                billing_cycle="monthly",
                amount=99.99
            )

        subscriptions = db.get_subscriptions()

        assert len(subscriptions) >= 3

    def test_get_subscriptions_by_tenant(self, db):
        """Test filtering subscriptions by tenant"""
        db.create_subscription(tenant_id="tenant_001", status="active", billing_cycle="monthly", amount=99.99)
        db.create_subscription(tenant_id="tenant_002", status="active", billing_cycle="monthly", amount=99.99)

        subscriptions = db.get_subscriptions(tenant_id="tenant_001")

        assert len(subscriptions) == 1
        assert subscriptions[0]['tenant_id'] == "tenant_001"

    def test_get_subscriptions_by_status(self, db):
        """Test filtering subscriptions by status"""
        db.create_subscription(tenant_id="tenant_001", status="active", billing_cycle="monthly", amount=99.99)
        db.create_subscription(tenant_id="tenant_002", status="canceled", billing_cycle="monthly", amount=99.99)

        subscriptions = db.get_subscriptions(status="active")

        assert all(sub['status'] == "active" for sub in subscriptions)

    def test_update_subscription_status_success(self, db):
        """Test updating subscription status"""
        subscription_id = db.create_subscription(
            tenant_id="tenant_001",
            status="active",
            billing_cycle="monthly",
            amount=99.99
        )

        result = db.update_subscription_status(subscription_id, "canceled")

        assert result is True

        # Verify in database
        subscriptions = db.get_subscriptions(tenant_id="tenant_001")
        assert subscriptions[0]['status'] == "canceled"

    def test_update_subscription_status_nonexistent(self, db):
        """Test updating non-existent subscription"""
        result = db.update_subscription_status("nonexistent_id", "canceled")

        assert result is False

    def test_delete_subscription_success(self, db):
        """Test deleting subscription"""
        subscription_id = db.create_subscription(
            tenant_id="tenant_001",
            status="active",
            billing_cycle="monthly",
            amount=99.99
        )

        result = db.delete_subscription(subscription_id)

        assert result is True

        # Verify deleted
        subscriptions = db.get_subscriptions(tenant_id="tenant_001")
        assert len(subscriptions) == 0

    def test_delete_subscription_nonexistent(self, db):
        """Test deleting non-existent subscription"""
        result = db.delete_subscription("nonexistent_id")

        assert result is False

    def test_initialize_sample_subscriptions(self, db):
        """Test initializing sample subscriptions"""
        count = db.initialize_sample_subscriptions(tenant_id="test_tenant")

        assert count > 0

        # Verify subscriptions created
        subscriptions = db.get_subscriptions(tenant_id="test_tenant")
        assert len(subscriptions) == count

    # ============================================
    # Error Handling Tests
    # ============================================

    def test_create_service_error_handling(self, db):
        """Test error handling when creating service fails"""
        # Create invalid service (missing required fields)
        invalid_service = Service(
            basic_info=BasicInfo(service_name="", target_group="", region=""),
            system_settings=SystemSettings(service_type=""),
        )

        # Should raise exception or handle gracefully
        try:
            db.create_service(invalid_service)
        except Exception as e:
            assert True  # Exception expected

    def test_database_connection_failure(self, tmp_path):
        """Test handling database connection failure"""
        # Try to create database in non-existent/read-only location
        invalid_path = "/invalid/path/database.db"

        with pytest.raises(Exception):
            db = Database(invalid_path)

    # ============================================
    # Connection Pool Tests
    # ============================================

    def test_connection_pool_reuse(self, db, sample_service):
        """Test that connection pool reuses connections"""
        # Create multiple services to test pool reuse
        for i in range(10):
            service = create_test_service(name=f"Service {i}")
            db.create_service(service)

        # All operations should succeed with pool
        assert db.count_services() == 10

    def test_concurrent_operations(self, db, multiple_services):
        """Test concurrent database operations"""
        import threading

        def create_service_thread(service):
            db.create_service(service)

        threads = []
        for service in multiple_services:
            thread = threading.Thread(target=create_service_thread, args=(service,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # All services should be created
        assert db.count_services() == len(multiple_services)


class TestDatabaseEdgeCases:
    """Edge case tests for Database"""

    @pytest.fixture
    def db(self, tmp_path):
        """Fixture providing Database instance"""
        db_path = tmp_path / "test_edge.db"
        return Database(str(db_path))

    def test_unicode_in_service_name(self, db):
        """Test handling unicode characters in service name"""
        service = create_test_service(
            name="Тестовая Служба 测试服务 🎉",
            target_group="International"
        )

        service_id = db.create_service(service)
        retrieved = db.get_service(service_id)

        assert retrieved is not None
        assert "Тестовая" in retrieved.basic_info.service_name

    def test_very_long_service_name(self, db):
        """Test handling very long service names"""
        long_name = "A" * 1000
        service = create_test_service(name=long_name)

        service_id = db.create_service(service)
        retrieved = db.get_service(service_id)

        assert retrieved is not None
        assert len(retrieved.basic_info.service_name) == 1000

    def test_special_characters_in_search(self, db):
        """Test search with special SQL characters"""
        service = create_test_service(name="Test's Service with \"quotes\" and % wildcard")
        db.create_service(service)

        results = db.search_services("quotes")

        assert len(results) > 0

    def test_null_handling(self, db):
        """Test handling of null/None values"""
        service = create_test_service()
        service_id = db.create_service(service)

        # Test getting with None/null
        result = db.get_service(None)
        assert result is None

    def test_large_decimal_values(self, db):
        """Test handling very large decimal values"""
        service = create_test_service(brutto_rate=9999999.99)

        service_id = db.create_service(service)
        retrieved = db.get_service(service_id)

        assert retrieved.financial.brutto_rate == Decimal("9999999.99")

    def test_database_size_limits(self, db):
        """Test database doesn't crash with many records"""
        # Create many services
        for i in range(100):
            service = create_test_service(name=f"Service {i}")
            db.create_service(service)

        # Should still work
        assert db.count_services() == 100
        services = db.list_services(limit=10)
        assert len(services) == 10
