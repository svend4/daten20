"""
SQLAlchemy ORM Models for Database Tables

This module defines SQLAlchemy ORM models for all database tables
used in the Document Management System. These models are used by
Alembic for automatic migration generation.

Note: The project also uses a custom migration system in migrations.py
alongside Alembic for maximum flexibility.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Base class for all models
Base = declarative_base()


class Service(Base):
    """Service model - stores service configurations and metadata."""

    __tablename__ = "services"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)
    target_group = Column(String)
    region = Column(String, index=True)
    service_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(Integer, default=1)
    config_json = Column(Text, nullable=False)

    # Relationships
    financial_data = relationship("FinancialData", back_populates="service", cascade="all, delete-orphan")
    versions = relationship("Version", back_populates="service", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Service(id={self.id}, name='{self.name}', region='{self.region}')>"


class FinancialData(Base):
    """Financial data model - stores financial calculations and rates."""

    __tablename__ = "financial_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False, index=True)
    brutto_rate = Column(Float, nullable=False)
    final_hourly_rate = Column(Float)
    calculation_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    service = relationship("Service", back_populates="financial_data")

    def __repr__(self):
        return f"<FinancialData(id={self.id}, service_id={self.service_id}, rate={self.brutto_rate})>"


class Version(Base):
    """Version model - stores version history for services."""

    __tablename__ = "versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    config_snapshot = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)
    change_notes = Column(Text)

    # Relationships
    service = relationship("Service", back_populates="versions")

    def __repr__(self):
        return f"<Version(id={self.id}, service_id={self.service_id}, version={self.version_number})>"


class Subscription(Base):
    """Subscription model - stores subscription data for BI dashboard."""

    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="active", index=True)
    billing_cycle = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="EUR")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    canceled_at = Column(DateTime, nullable=True)
    metadata_json = Column(Text, default="{}")

    def __repr__(self):
        return f"<Subscription(id='{self.id}', tenant='{self.tenant_id}', status='{self.status}')>"


class BillingTransaction(Base):
    """Billing transaction model - stores billing transaction history."""

    __tablename__ = "billing_transactions"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    subscription_id = Column(String, ForeignKey("subscriptions.id"), nullable=True, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="EUR")
    status = Column(String, nullable=False, default="pending", index=True)
    transaction_type = Column(String, nullable=False)
    payment_method = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata_json = Column(Text, default="{}")

    def __repr__(self):
        return f"<BillingTransaction(id='{self.id}', user='{self.user_id}', amount={self.amount})>"


class Document(Base):
    """Document model - stores document metadata and content."""

    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    tenant_id = Column(String, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String)
    status = Column(String, default="uploaded", index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    metadata_json = Column(Text, default="{}")

    # Relationships
    entities = relationship("Entity", back_populates="document", cascade="all, delete-orphan")
    classifications = relationship("Classification", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document(id='{self.id}', filename='{self.filename}', status='{self.status}')>"


class Entity(Base):
    """Entity model - stores extracted named entities from documents."""

    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = Column(String, nullable=False, index=True)
    entity_text = Column(String, nullable=False)
    start_char = Column(Integer)
    end_char = Column(Integer)
    confidence = Column(Float)
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="entities")

    def __repr__(self):
        return f"<Entity(id={self.id}, type='{self.entity_type}', text='{self.entity_text}')>"


class Classification(Base):
    """Classification model - stores document classifications."""

    __tablename__ = "classifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    model_version = Column(String)
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="classifications")

    def __repr__(self):
        return f"<Classification(id={self.id}, category='{self.category}', confidence={self.confidence})>"


class User(Base):
    """User model - stores user account information."""

    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, nullable=False, unique=True, index=True)
    username = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Integer, default=1)
    is_admin = Column(Integer, default=0)
    tenant_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    metadata_json = Column(Text, default="{}")

    def __repr__(self):
        return f"<User(id='{self.id}', username='{self.username}', email='{self.email}')>"


# Metadata export for Alembic
def get_metadata():
    """Get SQLAlchemy metadata for all models."""
    return Base.metadata


def create_all_tables(engine):
    """Create all tables in the database."""
    Base.metadata.create_all(engine)


def drop_all_tables(engine):
    """Drop all tables from the database."""
    Base.metadata.drop_all(engine)
