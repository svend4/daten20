"""
Comprehensive unit tests for core.database module

Test coverage goals:
- All Database methods with real functionality tests
- Positive cases: Normal operation
- Negative cases: Error handling
- Edge cases: Boundary conditions
- Integration: Connection pooling and migrations
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.core.database import Database
from src.models.financial import CostBreakdown, FinancialParameters
from src.models.service import BasicInfo, Service, SystemSettings

# Test markers
pytestmark = pytest.mark.unit


def create_test_service(name="Test Service", target_group="Youth", region="Berlin", service_type="counseling", brutto_rate=50.0):
    """Helper function to create a test service with proper structure"""
    from decimal import Decimal

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


class TestDatabaseInitialization:
    """Tests for Database initialization"""

    @pytest.fixture
    def temp_db_path(self, tmp_path):
        """Fixture providing temporary database path"""
        return str(tmp_path / "test.db")

    def test_database_initialization_creates_file(self, temp_db_path):
        """Test database file is created on initialization"""
        db = Database(temp_db_path, pool_size=2)
        assert Path(temp_db_path).exists()
        assert db.db_path == temp_db_path

    def test_database_creates_all_tables(self, temp_db_path):
        """Test all required tables are created"""
        db = Database(temp_db_path)

        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.cursor()

            # Check services table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='services'")
            assert cursor.fetchone() is not None

            # Check financial_data table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='financial_data'")
            assert cursor.fetchone() is not None

            # Check versions table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='versions'")
            assert cursor.fetchone() is not None

            # Check subscriptions table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='subscriptions'")
            assert cursor.fetchone() is not None

    def test_database_creates_indexes(self, temp_db_path):
        """Test database indexes are created"""
        db = Database(temp_db_path)

        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.cursor()

            # Get all indexes
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = [row[0] for row in cursor.fetchall()]

            # Check key indexes exist
            assert "idx_services_name" in indexes
            assert "idx_services_region" in indexes
            assert "idx_financial_service" in indexes

    def test_database_with_custom_pool_size(self, temp_db_path):
        """Test database initialization with custom pool size"""
        db = Database(temp_db_path, pool_size=10)
        assert db.pool is not None

    @patch("src.core.database.MigrationManager")
    def test_migrations_run_on_init(self, mock_migration_manager, temp_db_path):
        """Test migrations are checked and run on initialization"""
        mock_manager_instance = MagicMock()
        mock_migration_manager.return_value = mock_manager_instance

        db = Database(temp_db_path)

        # Verify migrations were checked
        mock_manager_instance.get_current_version.assert_called_once()
        mock_manager_instance.get_pending_migrations.assert_called_once()


class TestServiceOperations:
    """Tests for Service CRUD operations"""

    @pytest.fixture
    def db(self, tmp_path):
        """Fixture providing Database instance"""
        db_path = tmp_path / "test_services.db"
        return Database(str(db_path))

    @pytest.fixture
    def sample_service(self):
        """Fixture providing sample Service object"""
        from decimal import Decimal

        service = Service(
            basic_info=BasicInfo(
                service_name="Test Service",
                target_group="Youth",
                region="Berlin",
            ),
            system_settings=SystemSettings(
                service_type="counseling",
            ),
        )
        # Set financial parameters
        service.financial.brutto_rate = Decimal("50.0")
        return service

    def test_create_service_success(self, db, sample_service):
        """Test creating a new service"""
        service_id = db.create_service(sample_service)

        assert service_id is not None
        assert service_id > 0
        assert sample_service.id == service_id

    def test_create_service_stores_all_data(self, db, sample_service):
        """Test service creation stores all data correctly"""
        service_id = db.create_service(sample_service)

        # Verify in database
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()

            # Check services table
            cursor.execute("SELECT name, target_group, region, service_type FROM services WHERE id = ?", (service_id,))
            row = cursor.fetchone()
            assert row[0] == "Test Service"
            assert row[1] == "Youth"
            assert row[2] == "Berlin"
            assert row[3] == "counseling"

            # Check financial data
            cursor.execute("SELECT brutto_rate FROM financial_data WHERE service_id = ?", (service_id,))
            financial_row = cursor.fetchone()
            assert financial_row[0] == 50.0

            # Check version created
            cursor.execute("SELECT version_number FROM versions WHERE service_id = ?", (service_id,))
            version_row = cursor.fetchone()
            assert version_row[0] == 1

    def test_get_service_by_id(self, db, sample_service):
        """Test retrieving service by ID"""
        service_id = db.create_service(sample_service)

        retrieved = db.get_service(service_id)

        assert retrieved is not None
        assert retrieved.basic_info.service_name == "Test Service"
        assert retrieved.basic_info.target_group == "Youth"
        assert retrieved.financial.brutto_rate == 50.0

    def test_get_nonexistent_service(self, db):
        """Test getting non-existent service returns None"""
        retrieved = db.get_service(9999)
        assert retrieved is None

    def test_update_service_success(self, db, sample_service):
        """Test updating an existing service"""
        service_id = db.create_service(sample_service)

        # Update service
        sample_service.basic_info.service_name = "Updated Service"
        sample_service.financial.brutto_rate = 60.0

        success = db.update_service(sample_service)

        assert success is True

        # Verify update
        retrieved = db.get_service(service_id)
        assert retrieved.basic_info.service_name == "Updated Service"
        assert retrieved.financial.brutto_rate == 60.0

    def test_update_service_increments_version(self, db, sample_service):
        """Test updating service increments version number"""
        service_id = db.create_service(sample_service)
        original_version = sample_service.version

        sample_service.basic_info.service_name = "Updated"
        db.update_service(sample_service)

        assert sample_service.version == original_version + 1

    def test_update_service_without_id_fails(self, db):
        """Test updating service without ID fails"""
        service = create_test_service(name="Test", target_group="Youth", region="Berlin", brutto_rate=50.0, service_type="counseling")
        service.id = None

        result = db.update_service(service)
        assert result is False

    def test_delete_service_success(self, db, sample_service):
        """Test deleting a service"""
        service_id = db.create_service(sample_service)

        deleted = db.delete_service(service_id)

        assert deleted is True

        # Verify deletion
        retrieved = db.get_service(service_id)
        assert retrieved is None

    def test_delete_nonexistent_service(self, db):
        """Test deleting non-existent service returns False"""
        deleted = db.delete_service(9999)
        assert deleted is False

    def test_delete_service_cascades(self, db, sample_service):
        """Test deleting service also deletes related data (cascade)"""
        service_id = db.create_service(sample_service)

        db.delete_service(service_id)

        # Check financial data deleted
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM financial_data WHERE service_id = ?", (service_id,))
            count = cursor.fetchone()[0]
            assert count == 0


class TestServiceListing:
    """Tests for listing and searching services"""

    @pytest.fixture
    def db_with_services(self, tmp_path):
        """Fixture providing database with multiple services"""
        db = Database(str(tmp_path / "test_listing.db"))

        # Create multiple services
        for i in range(10):
            service = create_test_service(
                name=f"Service {i}",
                target_group="Youth" if i % 2 == 0 else "Elderly",
                region="Berlin" if i % 3 == 0 else "Hamburg",
                service_type="counseling" if i % 2 == 0 else "therapy",
                brutto_rate=50.0 + i
            )
            db.create_service(service)

        return db

    def test_list_all_services(self, db_with_services):
        """Test listing all services"""
        services = db_with_services.list_services(limit=100)

        assert len(services) == 10

    def test_list_services_with_limit(self, db_with_services):
        """Test listing services with limit"""
        services = db_with_services.list_services(limit=5)

        assert len(services) == 5

    def test_list_services_with_offset(self, db_with_services):
        """Test listing services with offset"""
        first_page = db_with_services.list_services(limit=5, offset=0)
        second_page = db_with_services.list_services(limit=5, offset=5)

        assert len(first_page) == 5
        assert len(second_page) == 5
        # Services should be different
        assert first_page[0].basic_info.service_name != second_page[0].basic_info.service_name

    def test_list_services_filter_by_region(self, db_with_services):
        """Test filtering services by region"""
        berlin_services = db_with_services.list_services(region="Berlin")

        assert len(berlin_services) > 0
        for service in berlin_services:
            assert service.basic_info.region == "Berlin"

    def test_list_services_filter_by_type(self, db_with_services):
        """Test filtering services by service type"""
        counseling_services = db_with_services.list_services(service_type="counseling")

        assert len(counseling_services) > 0
        for service in counseling_services:
            assert service.system_settings.service_type == "counseling"

    def test_list_services_multiple_filters(self, db_with_services):
        """Test filtering services by multiple criteria"""
        filtered = db_with_services.list_services(region="Berlin", service_type="counseling")

        for service in filtered:
            assert service.basic_info.region == "Berlin"
            assert service.system_settings.service_type == "counseling"

    def test_search_services_by_name(self, db_with_services):
        """Test searching services by name"""
        results = db_with_services.search_services("Service 5")

        assert len(results) >= 1
        assert any("Service 5" in s.basic_info.service_name for s in results)

    def test_search_services_by_target_group(self, db_with_services):
        """Test searching services by target group"""
        results = db_with_services.search_services("Youth")

        assert len(results) > 0
        assert all("Youth" in s.basic_info.target_group for s in results)

    def test_search_services_partial_match(self, db_with_services):
        """Test search with partial match"""
        results = db_with_services.search_services("Serv")

        # Should match "Service 0", "Service 1", etc.
        assert len(results) >= 10

    def test_search_services_no_results(self, db_with_services):
        """Test search with no matching results"""
        results = db_with_services.search_services("NonexistentService")

        assert len(results) == 0


class TestVersionManagement:
    """Tests for service version management"""

    @pytest.fixture
    def db(self, tmp_path):
        """Fixture providing Database instance"""
        return Database(str(tmp_path / "test_versions.db"))

    def test_get_service_versions(self, db):
        """Test retrieving service version history"""
        # Create service
        service = create_test_service(name="Test", target_group="Youth", region="Berlin", brutto_rate=50.0, service_type="counseling")
        service_id = db.create_service(service)

        # Update service multiple times
        for i in range(3):
            service.basic_info.service_name = f"Test v{i+2}"
            db.update_service(service)

        # Get versions
        versions = db.get_service_versions(service_id)

        assert len(versions) == 4  # Initial + 3 updates
        assert versions[0]["version"] == 4  # Latest first
        assert versions[-1]["version"] == 1  # Oldest last

    def test_version_includes_metadata(self, db):
        """Test version records include metadata"""
        service = create_test_service(name="Test", target_group="Youth", region="Berlin", brutto_rate=50.0, service_type="counseling")
        service_id = db.create_service(service)

        versions = db.get_service_versions(service_id)

        assert len(versions) > 0
        for version in versions:
            assert "version" in version
            assert "created_at" in version
            assert "notes" in version


class TestSubscriptionOperations:
    """Tests for subscription management"""

    @pytest.fixture
    def db(self, tmp_path):
        """Fixture providing Database instance"""
        return Database(str(tmp_path / "test_subscriptions.db"))

    def test_create_subscription(self, db):
        """Test creating a subscription"""
        success = db.create_subscription(
            subscription_id="sub_001",
            tenant_id="tenant_001",
            billing_cycle="monthly",
            amount=99.0,
            status="active",
            currency="EUR",
            metadata={"plan": "professional"},
        )

        assert success is True

    def test_create_duplicate_subscription_fails(self, db):
        """Test creating duplicate subscription fails"""
        db.create_subscription(
            subscription_id="sub_001",
            tenant_id="tenant_001",
            billing_cycle="monthly",
            amount=99.0,
        )

        # Try to create duplicate
        success = db.create_subscription(
            subscription_id="sub_001",
            tenant_id="tenant_001",
            billing_cycle="monthly",
            amount=99.0,
        )

        assert success is False

    def test_get_all_subscriptions(self, db):
        """Test getting all subscriptions"""
        # Create multiple subscriptions
        for i in range(5):
            db.create_subscription(
                subscription_id=f"sub_{i}",
                tenant_id="tenant_001",
                billing_cycle="monthly",
                amount=99.0 + i,
            )

        subscriptions = db.get_subscriptions()

        assert len(subscriptions) == 5

    def test_get_subscriptions_by_tenant(self, db):
        """Test filtering subscriptions by tenant"""
        db.create_subscription("sub_1", "tenant_001", "monthly", 99.0)
        db.create_subscription("sub_2", "tenant_002", "monthly", 99.0)

        tenant1_subs = db.get_subscriptions(tenant_id="tenant_001")
        tenant2_subs = db.get_subscriptions(tenant_id="tenant_002")

        assert len(tenant1_subs) == 1
        assert len(tenant2_subs) == 1
        assert tenant1_subs[0]["tenant_id"] == "tenant_001"

    def test_get_subscriptions_by_status(self, db):
        """Test filtering subscriptions by status"""
        db.create_subscription("sub_1", "tenant_001", "monthly", 99.0, status="active")
        db.create_subscription("sub_2", "tenant_001", "monthly", 99.0, status="canceled")

        active_subs = db.get_subscriptions(status="active")
        canceled_subs = db.get_subscriptions(status="canceled")

        assert len(active_subs) == 1
        assert len(canceled_subs) == 1

    def test_update_subscription_status(self, db):
        """Test updating subscription status"""
        db.create_subscription("sub_001", "tenant_001", "monthly", 99.0, status="active")

        success = db.update_subscription_status("sub_001", "canceled")

        assert success is True

        # Verify update
        subs = db.get_subscriptions(status="canceled")
        assert len(subs) == 1
        assert subs[0]["id"] == "sub_001"

    def test_update_nonexistent_subscription(self, db):
        """Test updating non-existent subscription returns False"""
        success = db.update_subscription_status("nonexistent", "canceled")

        assert success is False

    def test_delete_subscription(self, db):
        """Test deleting a subscription"""
        db.create_subscription("sub_001", "tenant_001", "monthly", 99.0)

        deleted = db.delete_subscription("sub_001")

        assert deleted is True

        # Verify deletion
        subs = db.get_subscriptions()
        assert len(subs) == 0

    def test_delete_nonexistent_subscription(self, db):
        """Test deleting non-existent subscription returns False"""
        deleted = db.delete_subscription("nonexistent")

        assert deleted is False

    def test_subscription_metadata_stored(self, db):
        """Test subscription metadata is stored and retrieved correctly"""
        metadata = {"plan": "professional", "users": 5, "features": ["api", "analytics"]}

        db.create_subscription(
            subscription_id="sub_001",
            tenant_id="tenant_001",
            billing_cycle="monthly",
            amount=99.0,
            metadata=metadata,
        )

        subs = db.get_subscriptions()

        assert len(subs) == 1
        assert subs[0]["metadata"] == metadata


class TestDatabaseStatistics:
    """Tests for database statistics"""

    @pytest.fixture
    def db_with_data(self, tmp_path):
        """Fixture providing database with sample data"""
        db = Database(str(tmp_path / "test_stats.db"))

        # Create services with different regions and types
        for i in range(15):
            service = create_test_service(
                name=f"Service {i}",
                target_group="Youth",
                region=["Berlin", "Hamburg", "Munich"][i % 3],
                service_type=["counseling", "therapy"][i % 2],
                brutto_rate=50.0 + i * 5
            )
            db.create_service(service)

        return db

    def test_get_statistics_total_services(self, db_with_data):
        """Test getting total services count"""
        stats = db_with_data.get_statistics()

        assert stats["total_services"] == 15

    def test_get_statistics_by_region(self, db_with_data):
        """Test getting service counts by region"""
        stats = db_with_data.get_statistics()

        assert "by_region" in stats
        assert stats["by_region"]["Berlin"] == 5
        assert stats["by_region"]["Hamburg"] == 5
        assert stats["by_region"]["Munich"] == 5

    def test_get_statistics_by_type(self, db_with_data):
        """Test getting service counts by type"""
        stats = db_with_data.get_statistics()

        assert "by_type" in stats
        # Should have roughly equal distribution
        assert stats["by_type"]["counseling"] > 0
        assert stats["by_type"]["therapy"] > 0

    def test_get_statistics_average_rate(self, db_with_data):
        """Test getting average brutto rate"""
        stats = db_with_data.get_statistics()

        assert "avg_brutto_rate" in stats
        assert stats["avg_brutto_rate"] > 0
        # Average should be around middle of range (50 + 70) / 2 = ~85
        assert 80 < stats["avg_brutto_rate"] < 90

    def test_statistics_on_empty_database(self, tmp_path):
        """Test statistics on empty database"""
        db = Database(str(tmp_path / "empty.db"))
        stats = db.get_statistics()

        assert stats["total_services"] == 0
        assert stats["avg_brutto_rate"] == 0


class TestSampleDataInitialization:
    """Tests for sample data initialization"""

    @pytest.fixture
    def db(self, tmp_path):
        """Fixture providing Database instance"""
        return Database(str(tmp_path / "test_samples.db"))

    def test_initialize_sample_subscriptions(self, db):
        """Test initializing sample subscription data"""
        count = db.initialize_sample_subscriptions(tenant_id="test_tenant")

        assert count == 5  # 5 sample subscriptions

    def test_sample_subscriptions_have_correct_data(self, db):
        """Test sample subscriptions have expected data"""
        db.initialize_sample_subscriptions(tenant_id="test_tenant")

        subs = db.get_subscriptions(tenant_id="test_tenant")

        assert len(subs) == 5
        # Check for active subscriptions
        active_subs = [s for s in subs if s["status"] == "active"]
        assert len(active_subs) == 4
        # Check for canceled subscription
        canceled_subs = [s for s in subs if s["status"] == "canceled"]
        assert len(canceled_subs) == 1

    def test_initialize_sample_subscriptions_idempotent(self, db):
        """Test initializing samples multiple times doesn't create duplicates"""
        count1 = db.initialize_sample_subscriptions(tenant_id="test_tenant")
        count2 = db.initialize_sample_subscriptions(tenant_id="test_tenant")

        assert count1 == 5
        assert count2 == 0  # Should not create duplicates

        # Verify total count
        subs = db.get_subscriptions(tenant_id="test_tenant")
        assert len(subs) == 5


class TestErrorHandling:
    """Tests for error handling and edge cases"""

    @pytest.fixture
    def db(self, tmp_path):
        """Fixture providing Database instance"""
        return Database(str(tmp_path / "test_errors.db"))

    def test_create_service_with_invalid_data(self, db):
        """Test error handling with invalid service data"""
        # This should raise an exception
        with pytest.raises(Exception):
            db.create_service(None)

    def test_database_recovers_from_migration_errors(self, tmp_path):
        """Test database continues even if migrations fail"""
        with patch("src.core.database.MigrationManager") as mock_mgr:
            mock_instance = MagicMock()
            mock_instance.get_current_version.side_effect = Exception("Migration error")
            mock_mgr.return_value = mock_instance

            # Should not raise, just log warning
            db = Database(str(tmp_path / "test_migration_error.db"))
            assert db is not None

    def test_get_statistics_handles_empty_tables(self, db):
        """Test statistics work with empty tables"""
        stats = db.get_statistics()

        assert isinstance(stats, dict)
        assert stats["total_services"] == 0

    def test_list_services_with_zero_limit(self, db):
        """Test listing services with edge case limit"""
        services = db.list_services(limit=0)
        # Should return empty list or handle gracefully
        assert isinstance(services, list)


class TestConcurrency:
    """Tests for concurrent database access"""

    @pytest.fixture
    def db(self, tmp_path):
        """Fixture providing Database instance with connection pool"""
        return Database(str(tmp_path / "test_concurrent.db"), pool_size=5)

    def test_connection_pool_initialized(self, db):
        """Test connection pool is initialized"""
        assert db.pool is not None

    def test_multiple_operations_use_pool(self, db):
        """Test multiple operations can use connection pool"""
        services = []

        # Create multiple services
        for i in range(10):
            service = create_test_service(
                name=f"Service {i}",
                target_group="Youth",
                region="Berlin",
                service_type="counseling",
                brutto_rate=50.0
            )
            service_id = db.create_service(service)
            services.append(service_id)

        # All should be created successfully
        assert len(services) == 10

        # All should be retrievable
        for service_id in services:
            service = db.get_service(service_id)
            assert service is not None
