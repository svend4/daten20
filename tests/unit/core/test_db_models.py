"""
Unit tests for db_models (SQLAlchemy ORM models)
"""

import json
import os
import tempfile
from datetime import datetime

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker

from src.core.db_models import (
    Base,
    BillingTransaction,
    Classification,
    Document,
    Entity,
    FinancialData,
    Service,
    Subscription,
    User,
    Version,
    create_all_tables,
    drop_all_tables,
    get_metadata,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def in_memory_db():
    """Create in-memory SQLite database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db_session(in_memory_db):
    """Create database session"""
    SessionLocal = sessionmaker(bind=in_memory_db)
    session = SessionLocal()
    yield session
    session.close()


# ============================================================================
# Service Model Tests
# ============================================================================


class TestServiceModel:
    """Test Service ORM model"""

    def test_create_service(self, db_session):
        """Test creating a service"""
        service = Service(
            name="Test Service",
            target_group="Test Group",
            region="Berlin",
            service_type="social",
            config_json='{"key": "value"}',
        )

        db_session.add(service)
        db_session.commit()

        assert service.id is not None
        assert service.name == "Test Service"
        assert service.region == "Berlin"

    def test_service_defaults(self, db_session):
        """Test service default values"""
        service = Service(name="Test", config_json="{}")

        db_session.add(service)
        db_session.commit()

        assert service.version == 1
        assert service.created_at is not None
        assert service.updated_at is not None

    def test_service_repr(self, db_session):
        """Test service string representation"""
        service = Service(name="Test Service", region="Munich", config_json="{}")

        db_session.add(service)
        db_session.commit()

        repr_str = repr(service)

        assert "Service" in repr_str
        assert "Test Service" in repr_str
        assert "Munich" in repr_str

    def test_service_relationships(self, db_session):
        """Test service relationships"""
        service = Service(name="Test", config_json="{}")

        db_session.add(service)
        db_session.commit()

        # Relationships should be empty lists initially
        assert service.financial_data == []
        assert service.versions == []

    def test_service_with_financial_data(self, db_session):
        """Test service with associated financial data"""
        service = Service(name="Test", config_json="{}")
        db_session.add(service)
        db_session.commit()

        financial = FinancialData(service_id=service.id, brutto_rate=25.50)
        db_session.add(financial)
        db_session.commit()

        db_session.refresh(service)

        assert len(service.financial_data) == 1
        assert service.financial_data[0].brutto_rate == 25.50

    def test_service_cascade_delete(self, db_session):
        """Test cascade delete of financial data"""
        service = Service(name="Test", config_json="{}")
        db_session.add(service)
        db_session.commit()

        financial = FinancialData(service_id=service.id, brutto_rate=25.50)
        db_session.add(financial)
        db_session.commit()

        service_id = service.id

        # Delete service
        db_session.delete(service)
        db_session.commit()

        # Financial data should be deleted too
        result = db_session.query(FinancialData).filter_by(service_id=service_id).first()
        assert result is None


# ============================================================================
# FinancialData Model Tests
# ============================================================================


class TestFinancialDataModel:
    """Test FinancialData ORM model"""

    def test_create_financial_data(self, db_session):
        """Test creating financial data"""
        service = Service(name="Test", config_json="{}")
        db_session.add(service)
        db_session.commit()

        financial = FinancialData(
            service_id=service.id, brutto_rate=30.00, final_hourly_rate=45.00, calculation_json='{"test": "data"}'
        )

        db_session.add(financial)
        db_session.commit()

        assert financial.id is not None
        assert financial.brutto_rate == 30.00
        assert financial.final_hourly_rate == 45.00

    def test_financial_data_defaults(self, db_session):
        """Test financial data default values"""
        service = Service(name="Test", config_json="{}")
        db_session.add(service)
        db_session.commit()

        financial = FinancialData(service_id=service.id, brutto_rate=25.00)

        db_session.add(financial)
        db_session.commit()

        assert financial.created_at is not None

    def test_financial_data_repr(self, db_session):
        """Test financial data string representation"""
        service = Service(name="Test", config_json="{}")
        db_session.add(service)
        db_session.commit()

        financial = FinancialData(service_id=service.id, brutto_rate=25.50)
        db_session.add(financial)
        db_session.commit()

        repr_str = repr(financial)

        assert "FinancialData" in repr_str
        assert "25.5" in repr_str or "25.50" in repr_str


# ============================================================================
# Version Model Tests
# ============================================================================


class TestVersionModel:
    """Test Version ORM model"""

    def test_create_version(self, db_session):
        """Test creating a version"""
        service = Service(name="Test", config_json="{}")
        db_session.add(service)
        db_session.commit()

        version = Version(
            service_id=service.id,
            version_number=1,
            config_snapshot='{"config": "v1"}',
            created_by="admin",
            change_notes="Initial version",
        )

        db_session.add(version)
        db_session.commit()

        assert version.id is not None
        assert version.version_number == 1
        assert version.created_by == "admin"

    def test_version_defaults(self, db_session):
        """Test version default values"""
        service = Service(name="Test", config_json="{}")
        db_session.add(service)
        db_session.commit()

        version = Version(service_id=service.id, version_number=1, config_snapshot="{}")

        db_session.add(version)
        db_session.commit()

        assert version.created_at is not None

    def test_version_repr(self, db_session):
        """Test version string representation"""
        service = Service(name="Test", config_json="{}")
        db_session.add(service)
        db_session.commit()

        version = Version(service_id=service.id, version_number=2, config_snapshot="{}")
        db_session.add(version)
        db_session.commit()

        repr_str = repr(version)

        assert "Version" in repr_str
        assert "2" in repr_str


# ============================================================================
# Subscription Model Tests
# ============================================================================


class TestSubscriptionModel:
    """Test Subscription ORM model"""

    def test_create_subscription(self, db_session):
        """Test creating a subscription"""
        subscription = Subscription(
            id="sub_123",
            tenant_id="tenant_1",
            billing_cycle="monthly",
            amount=99.99,
            currency="EUR",
            status="active",
        )

        db_session.add(subscription)
        db_session.commit()

        assert subscription.id == "sub_123"
        assert subscription.amount == 99.99
        assert subscription.status == "active"

    def test_subscription_defaults(self, db_session):
        """Test subscription default values"""
        subscription = Subscription(id="sub_123", tenant_id="tenant_1", billing_cycle="monthly", amount=99.99)

        db_session.add(subscription)
        db_session.commit()

        assert subscription.status == "active"
        assert subscription.currency == "EUR"
        assert subscription.created_at is not None
        assert subscription.metadata_json == "{}"

    def test_subscription_repr(self, db_session):
        """Test subscription string representation"""
        subscription = Subscription(
            id="sub_123", tenant_id="tenant_1", billing_cycle="monthly", amount=99.99, status="active"
        )
        db_session.add(subscription)
        db_session.commit()

        repr_str = repr(subscription)

        assert "Subscription" in repr_str
        assert "sub_123" in repr_str
        assert "active" in repr_str


# ============================================================================
# BillingTransaction Model Tests
# ============================================================================


class TestBillingTransactionModel:
    """Test BillingTransaction ORM model"""

    def test_create_billing_transaction(self, db_session):
        """Test creating a billing transaction"""
        transaction = BillingTransaction(
            id="tx_123",
            user_id="user_1",
            amount=49.99,
            currency="EUR",
            status="completed",
            transaction_type="payment",
            payment_method="card",
        )

        db_session.add(transaction)
        db_session.commit()

        assert transaction.id == "tx_123"
        assert transaction.amount == 49.99
        assert transaction.status == "completed"

    def test_billing_transaction_defaults(self, db_session):
        """Test billing transaction default values"""
        transaction = BillingTransaction(
            id="tx_123", user_id="user_1", amount=49.99, transaction_type="payment"
        )

        db_session.add(transaction)
        db_session.commit()

        assert transaction.status == "pending"
        assert transaction.currency == "EUR"
        assert transaction.created_at is not None
        assert transaction.metadata_json == "{}"

    def test_billing_transaction_repr(self, db_session):
        """Test billing transaction string representation"""
        transaction = BillingTransaction(id="tx_123", user_id="user_1", amount=49.99, transaction_type="payment")
        db_session.add(transaction)
        db_session.commit()

        repr_str = repr(transaction)

        assert "BillingTransaction" in repr_str
        assert "tx_123" in repr_str
        assert "49.99" in repr_str


# ============================================================================
# Document Model Tests
# ============================================================================


class TestDocumentModel:
    """Test Document ORM model"""

    def test_create_document(self, db_session):
        """Test creating a document"""
        document = Document(
            id="doc_123",
            user_id="user_1",
            tenant_id="tenant_1",
            filename="test.pdf",
            file_path="/path/to/test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            status="uploaded",
        )

        db_session.add(document)
        db_session.commit()

        assert document.id == "doc_123"
        assert document.filename == "test.pdf"
        assert document.status == "uploaded"

    def test_document_defaults(self, db_session):
        """Test document default values"""
        document = Document(
            id="doc_123", user_id="user_1", filename="test.pdf", file_path="/path/to/test.pdf"
        )

        db_session.add(document)
        db_session.commit()

        assert document.status == "uploaded"
        assert document.created_at is not None
        assert document.metadata_json == "{}"

    def test_document_repr(self, db_session):
        """Test document string representation"""
        document = Document(
            id="doc_123", user_id="user_1", filename="report.pdf", file_path="/path", status="processed"
        )
        db_session.add(document)
        db_session.commit()

        repr_str = repr(document)

        assert "Document" in repr_str
        assert "doc_123" in repr_str
        assert "report.pdf" in repr_str
        assert "processed" in repr_str

    def test_document_relationships(self, db_session):
        """Test document relationships"""
        document = Document(id="doc_123", user_id="user_1", filename="test.pdf", file_path="/path")

        db_session.add(document)
        db_session.commit()

        # Relationships should be empty initially
        assert document.entities == []
        assert document.classifications == []

    def test_document_with_entities(self, db_session):
        """Test document with associated entities"""
        document = Document(id="doc_123", user_id="user_1", filename="test.pdf", file_path="/path")
        db_session.add(document)
        db_session.commit()

        entity = Entity(
            document_id=document.id, entity_type="PERSON", entity_text="John Doe", start_char=0, end_char=8
        )
        db_session.add(entity)
        db_session.commit()

        db_session.refresh(document)

        assert len(document.entities) == 1
        assert document.entities[0].entity_text == "John Doe"


# ============================================================================
# Entity Model Tests
# ============================================================================


class TestEntityModel:
    """Test Entity ORM model"""

    def test_create_entity(self, db_session):
        """Test creating an entity"""
        document = Document(id="doc_123", user_id="user_1", filename="test.pdf", file_path="/path")
        db_session.add(document)
        db_session.commit()

        entity = Entity(
            document_id=document.id,
            entity_type="ORGANIZATION",
            entity_text="Acme Corp",
            start_char=10,
            end_char=19,
            confidence=0.95,
        )

        db_session.add(entity)
        db_session.commit()

        assert entity.id is not None
        assert entity.entity_type == "ORGANIZATION"
        assert entity.confidence == 0.95

    def test_entity_defaults(self, db_session):
        """Test entity default values"""
        document = Document(id="doc_123", user_id="user_1", filename="test.pdf", file_path="/path")
        db_session.add(document)
        db_session.commit()

        entity = Entity(document_id=document.id, entity_type="PERSON", entity_text="John")

        db_session.add(entity)
        db_session.commit()

        assert entity.created_at is not None
        assert entity.metadata_json == "{}"

    def test_entity_repr(self, db_session):
        """Test entity string representation"""
        document = Document(id="doc_123", user_id="user_1", filename="test.pdf", file_path="/path")
        db_session.add(document)
        db_session.commit()

        entity = Entity(document_id=document.id, entity_type="LOCATION", entity_text="Berlin")
        db_session.add(entity)
        db_session.commit()

        repr_str = repr(entity)

        assert "Entity" in repr_str
        assert "LOCATION" in repr_str
        assert "Berlin" in repr_str


# ============================================================================
# Classification Model Tests
# ============================================================================


class TestClassificationModel:
    """Test Classification ORM model"""

    def test_create_classification(self, db_session):
        """Test creating a classification"""
        document = Document(id="doc_123", user_id="user_1", filename="test.pdf", file_path="/path")
        db_session.add(document)
        db_session.commit()

        classification = Classification(
            document_id=document.id, category="invoice", confidence=0.98, model_version="v1.2.3"
        )

        db_session.add(classification)
        db_session.commit()

        assert classification.id is not None
        assert classification.category == "invoice"
        assert classification.confidence == 0.98

    def test_classification_defaults(self, db_session):
        """Test classification default values"""
        document = Document(id="doc_123", user_id="user_1", filename="test.pdf", file_path="/path")
        db_session.add(document)
        db_session.commit()

        classification = Classification(document_id=document.id, category="contract", confidence=0.85)

        db_session.add(classification)
        db_session.commit()

        assert classification.created_at is not None
        assert classification.metadata_json == "{}"

    def test_classification_repr(self, db_session):
        """Test classification string representation"""
        document = Document(id="doc_123", user_id="user_1", filename="test.pdf", file_path="/path")
        db_session.add(document)
        db_session.commit()

        classification = Classification(document_id=document.id, category="invoice", confidence=0.95)
        db_session.add(classification)
        db_session.commit()

        repr_str = repr(classification)

        assert "Classification" in repr_str
        assert "invoice" in repr_str
        assert "0.95" in repr_str


# ============================================================================
# User Model Tests
# ============================================================================


class TestUserModel:
    """Test User ORM model"""

    def test_create_user(self, db_session):
        """Test creating a user"""
        user = User(
            id="user_123",
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            full_name="Test User",
        )

        db_session.add(user)
        db_session.commit()

        assert user.id == "user_123"
        assert user.email == "test@example.com"
        assert user.username == "testuser"

    def test_user_defaults(self, db_session):
        """Test user default values"""
        user = User(id="user_123", email="test@example.com", username="testuser", password_hash="hashed")

        db_session.add(user)
        db_session.commit()

        assert user.is_active == 1
        assert user.is_admin == 0
        assert user.created_at is not None
        assert user.metadata_json == "{}"

    def test_user_repr(self, db_session):
        """Test user string representation"""
        user = User(id="user_123", email="admin@example.com", username="admin", password_hash="hashed")
        db_session.add(user)
        db_session.commit()

        repr_str = repr(user)

        assert "User" in repr_str
        assert "user_123" in repr_str
        assert "admin" in repr_str


# ============================================================================
# Helper Function Tests
# ============================================================================


class TestHelperFunctions:
    """Test helper functions"""

    def test_get_metadata(self):
        """Test getting metadata"""
        metadata = get_metadata()

        assert metadata is not None
        assert "services" in metadata.tables
        assert "users" in metadata.tables
        assert "documents" in metadata.tables

    def test_create_all_tables(self):
        """Test creating all tables"""
        engine = create_engine("sqlite:///:memory:")

        create_all_tables(engine)

        # Verify tables exist
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        assert "services" in tables
        assert "users" in tables
        assert "documents" in tables

        engine.dispose()

    def test_drop_all_tables(self):
        """Test dropping all tables"""
        engine = create_engine("sqlite:///:memory:")

        create_all_tables(engine)
        drop_all_tables(engine)

        # Verify tables don't exist
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        assert len(tables) == 0

        engine.dispose()


# ============================================================================
# Integration Tests
# ============================================================================


class TestDatabaseIntegration:
    """Test database integration scenarios"""

    def test_complete_service_workflow(self, db_session):
        """Test complete service creation workflow"""
        # Create service
        service = Service(name="Complete Service", region="Berlin", config_json='{"test": true}')
        db_session.add(service)
        db_session.commit()

        # Add financial data
        financial = FinancialData(service_id=service.id, brutto_rate=35.00, final_hourly_rate=52.50)
        db_session.add(financial)
        db_session.commit()

        # Add version
        version = Version(
            service_id=service.id, version_number=1, config_snapshot='{"v": 1}', created_by="admin"
        )
        db_session.add(version)
        db_session.commit()

        # Verify all data
        db_session.refresh(service)

        assert service.name == "Complete Service"
        assert len(service.financial_data) == 1
        assert len(service.versions) == 1

    def test_complete_document_workflow(self, db_session):
        """Test complete document processing workflow"""
        # Create document
        document = Document(id="doc_workflow", user_id="user_1", filename="test.pdf", file_path="/path")
        db_session.add(document)
        db_session.commit()

        # Add entities
        entity1 = Entity(document_id=document.id, entity_type="PERSON", entity_text="John Doe")
        entity2 = Entity(document_id=document.id, entity_type="ORG", entity_text="Acme Corp")
        db_session.add_all([entity1, entity2])
        db_session.commit()

        # Add classification
        classification = Classification(document_id=document.id, category="invoice", confidence=0.95)
        db_session.add(classification)
        db_session.commit()

        # Verify all data
        db_session.refresh(document)

        assert len(document.entities) == 2
        assert len(document.classifications) == 1

    def test_query_with_filters(self, db_session):
        """Test querying with filters"""
        # Create multiple services
        for i in range(5):
            service = Service(name=f"Service {i}", region="Berlin" if i < 3 else "Munich", config_json="{}")
            db_session.add(service)

        db_session.commit()

        # Query by region
        berlin_services = db_session.query(Service).filter_by(region="Berlin").all()

        assert len(berlin_services) == 3

    def test_update_timestamps(self, db_session):
        """Test automatic timestamp updates"""
        service = Service(name="Test", config_json="{}")
        db_session.add(service)
        db_session.commit()

        original_updated_at = service.updated_at

        # Update service
        service.name = "Updated Test"
        db_session.commit()

        db_session.refresh(service)

        # updated_at should change
        assert service.updated_at >= original_updated_at
