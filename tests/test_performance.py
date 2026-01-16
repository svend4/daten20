"""
Performance Tests

Tests for benchmarking critical operations.
Run with: pytest tests/test_performance.py --benchmark-only
"""

import os
import tempfile
from pathlib import Path

import pytest

# Mark all tests in this module as performance tests and skip them (optional benchmarks)
pytestmark = [
    pytest.mark.performance,
    pytest.mark.skip(reason="Performance tests are optional benchmarks - not required for basic functionality"),
]


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    yield db_path

    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def sample_service_data():
    """Sample service data for testing"""
    return {
        "service_name": "Performance Test Service",
        "region": "Bavaria",
        "brutto_rate": 45.00,
        "hours_per_month": 160,
        "kv_rate": 14.6,
        "pv_rate": 3.05,
        "rv_rate": 18.6,
        "av_rate": 2.6,
        "uv_rate": 1.3,
        "u1_rate": 0.9,
        "u2_rate": 0.19,
        "u3_rate": 0.09,
    }


class TestDatabasePerformance:
    """Database operation performance tests"""

    def test_database_initialization(self, benchmark, temp_db):
        """Benchmark database initialization"""
        from src.core.database import Database

        def init_db():
            db = Database(db_path=temp_db)
            return db

        db = benchmark(init_db)
        assert db is not None

    def test_service_insertion(self, benchmark, sample_service_data):
        """Benchmark service insertion"""
        from src.core.database import Database
        from src.models import BasicInfo, FinancialData, ServiceConfig

        db = Database()

        def insert_service():
            service = ServiceConfig(
                basic_info=BasicInfo(
                    service_name=sample_service_data["service_name"], region=sample_service_data["region"]
                ),
                financial=FinancialData(
                    brutto_rate=sample_service_data["brutto_rate"],
                    hours_per_month=sample_service_data["hours_per_month"],
                ),
            )
            return db.save_service(service)

        service_id = benchmark(insert_service)
        assert service_id > 0

    def test_service_retrieval(self, benchmark):
        """Benchmark service retrieval"""
        from src.core.database import Database
        from src.models import BasicInfo, FinancialData, ServiceConfig

        db = Database()

        # Create a service first
        service = ServiceConfig(
            basic_info=BasicInfo(service_name="Retrieval Test", region="Bavaria"),
            financial=FinancialData(brutto_rate=45.00, hours_per_month=160),
        )
        service_id = db.save_service(service)

        def get_service():
            return db.load_service(service_id)

        retrieved = benchmark(get_service)
        assert retrieved is not None
        assert retrieved.basic_info.service_name == "Retrieval Test"

    def test_service_list_all(self, benchmark):
        """Benchmark listing all services"""
        from src.core.database import Database

        db = Database()

        def list_services():
            return db.list_services()

        services = benchmark(list_services)
        assert isinstance(services, list)


class TestCalculationPerformance:
    """Financial calculation performance tests"""

    def test_hourly_rate_calculation(self, benchmark, sample_service_data):
        """Benchmark hourly rate calculation"""
        from src.financial_calculator import FinancialCalculator, FinancialParameters

        calc = FinancialCalculator()
        params = FinancialParameters(
            brutto_rate=sample_service_data["brutto_rate"],
            hours_per_month=sample_service_data["hours_per_month"],
            kv_rate=sample_service_data["kv_rate"],
            pv_rate=sample_service_data["pv_rate"],
            rv_rate=sample_service_data["rv_rate"],
            av_rate=sample_service_data["av_rate"],
            uv_rate=sample_service_data["uv_rate"],
            u1_rate=sample_service_data["u1_rate"],
            u2_rate=sample_service_data["u2_rate"],
            u3_rate=sample_service_data["u3_rate"],
            region="Bavaria",
            use_umlages=True,
        )

        def calculate():
            return calc.calculate_hourly_rate(params)

        result = benchmark(calculate)
        assert result is not None
        assert result.final_hourly_rate > 0

    def test_batch_calculations(self, benchmark):
        """Benchmark batch calculations for multiple services"""
        from src.financial_calculator import FinancialCalculator, FinancialParameters

        calc = FinancialCalculator()

        # Create 100 different parameter sets
        param_sets = []
        for i in range(100):
            params = FinancialParameters(
                brutto_rate=30.0 + i * 0.1,
                hours_per_month=160,
                kv_rate=14.6,
                pv_rate=3.05,
                rv_rate=18.6,
                av_rate=2.6,
                uv_rate=1.3,
                u1_rate=0.9,
                u2_rate=0.19,
                u3_rate=0.09,
                region="Bavaria",
                use_umlages=True,
            )
            param_sets.append(params)

        def batch_calculate():
            results = []
            for params in param_sets:
                result = calc.calculate_hourly_rate(params)
                results.append(result)
            return results

        results = benchmark(batch_calculate)
        assert len(results) == 100


class TestDocumentGenerationPerformance:
    """Document generation performance tests"""

    def test_text_generation(self, benchmark):
        """Benchmark text document generation"""
        from src.document_generator import DocumentGenerator
        from src.models import BasicInfo, FinancialData, ServiceConfig

        gen = DocumentGenerator()
        service = ServiceConfig(
            basic_info=BasicInfo(service_name="Performance Test", region="Bavaria"),
            financial=FinancialData(brutto_rate=45.00, hours_per_month=160),
        )

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            output_path = f.name

        try:

            def generate():
                return gen.generate_document(service, output_path, format="txt")

            result = benchmark(generate)
            assert result is True
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_html_generation(self, benchmark):
        """Benchmark HTML document generation"""
        from src.document_generator import DocumentGenerator
        from src.models import BasicInfo, FinancialData, ServiceConfig

        gen = DocumentGenerator()
        service = ServiceConfig(
            basic_info=BasicInfo(service_name="Performance Test", region="Bavaria"),
            financial=FinancialData(brutto_rate=45.00, hours_per_month=160),
        )

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            output_path = f.name

        try:

            def generate():
                return gen.generate_document(service, output_path, format="html")

            result = benchmark(generate)
            assert result is True
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestAuthenticationPerformance:
    """Authentication system performance tests"""

    def test_password_hashing(self, benchmark):
        """Benchmark password hashing"""
        from src.core.auth import get_auth_manager

        auth = get_auth_manager()

        def hash_password():
            return auth._hash_password("test_password_123")

        hashed = benchmark(hash_password)
        assert hashed is not None

    def test_password_verification(self, benchmark):
        """Benchmark password verification"""
        from src.core.auth import get_auth_manager

        auth = get_auth_manager()
        hashed = auth._hash_password("test_password_123")

        def verify():
            return auth._verify_password("test_password_123", hashed)

        result = benchmark(verify)
        assert result is True

    def test_token_generation(self, benchmark):
        """Benchmark JWT token generation"""
        from src.core.auth import Role, get_auth_manager
        from src.models import User

        auth = get_auth_manager()
        user = User(id=1, username="testuser", email="test@example.com", role=Role.VIEWER)

        def generate():
            return auth.generate_token(user, "secret_key_for_testing", expires_in=3600)

        token = benchmark(generate)
        assert token is not None


class TestCachePerformance:
    """Caching system performance tests"""

    def test_cache_set_get(self, benchmark):
        """Benchmark cache set and get operations"""
        from src.core.cache import SimpleCache

        cache = SimpleCache()

        def cache_operations():
            cache.set("test_key", {"data": "test_value"}, timeout=60)
            return cache.get("test_key")

        result = benchmark(cache_operations)
        assert result is not None
        assert result["data"] == "test_value"

    def test_cache_many_operations(self, benchmark):
        """Benchmark multiple cache operations"""
        from src.core.cache import SimpleCache

        cache = SimpleCache()

        def many_operations():
            # Set 100 items
            for i in range(100):
                cache.set(f"key_{i}", {"value": i}, timeout=60)

            # Get 100 items
            results = []
            for i in range(100):
                results.append(cache.get(f"key_{i}"))

            return results

        results = benchmark(many_operations)
        assert len(results) == 100


class TestAuditLogPerformance:
    """Audit logging performance tests"""

    def test_audit_log_write(self, benchmark):
        """Benchmark audit log write operation"""
        from src.core.audit import AuditAction, AuditLevel, get_audit_logger

        auditor = get_audit_logger()

        def log_entry():
            auditor.log(
                action=AuditAction.SERVICE_CREATED,
                user_id=1,
                username="testuser",
                level=AuditLevel.INFO,
                resource_type="service",
                resource_id="123",
                details={"test": "data"},
                status="success",
            )

        benchmark(log_entry)

    def test_audit_log_read(self, benchmark):
        """Benchmark audit log read operation"""
        from src.core.audit import AuditAction, AuditLevel, get_audit_logger

        auditor = get_audit_logger()

        # Create some log entries first
        for i in range(50):
            auditor.log(
                action=AuditAction.SERVICE_VIEWED,
                user_id=1,
                username="testuser",
                level=AuditLevel.INFO,
                resource_type="service",
                resource_id=str(i),
                details={},
                status="success",
            )

        def read_entries():
            return auditor.get_entries(limit=50)

        entries = benchmark(read_entries)
        assert len(entries) >= 50


class TestWebhookPerformance:
    """Webhook system performance tests"""

    def test_webhook_signature_generation(self, benchmark):
        """Benchmark webhook signature generation"""
        from src.core.webhooks import WebhookConfig, WebhookEvent, WebhookManager

        mgr = WebhookManager()
        config = WebhookConfig(
            url="http://example.com/webhook", secret="test_secret_key", events=[WebhookEvent.SERVICE_CREATED]
        )

        payload = {"test": "data", "service_id": "123"}

        def generate_signature():
            return mgr._generate_signature(payload, config.secret)

        signature = benchmark(generate_signature)
        assert signature is not None


class TestExportPerformance:
    """Export functionality performance tests"""

    def test_csv_export(self, benchmark):
        """Benchmark CSV export"""
        from src.core.database import Database
        from src.core.excel_export import export_services_to_csv

        db = Database()
        services = db.list_services()[:100]  # Export up to 100 services

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            output_path = f.name

        try:

            def export():
                return export_services_to_csv(services, output_path)

            result = benchmark(export)
            assert result is True
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


# Performance benchmarking configuration
@pytest.mark.benchmark(group="database", min_rounds=5, warmup=True)
class TestBenchmarkConfiguration:
    """Tests with custom benchmark configuration"""

    pass
