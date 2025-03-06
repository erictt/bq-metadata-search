"""
Database models for storing BigQuery metadata.
"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Index, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from dataclasses import dataclass
from typing import Optional

Base = declarative_base()

@dataclass
class Dataset:
    """Dataset metadata."""
    id: str
    full_id: str
    project_id: str
    friendly_name: str | None = None
    description: str | None = None


@dataclass
class Table:
    """Table metadata."""
    id: str
    full_id: str
    dataset_id: str
    project_id: str
    friendly_name: str | None = None
    description: str | None = None
    table_type: str | None = None


@dataclass
class Field:
    """Field metadata."""
    name: str
    full_id: str
    table_id: str
    dataset_id: str
    project_id: str
    field_type: str | None = None
    description: str | None = None
    mode: str | None = None


class DatasetModel(Base):
    """SQLAlchemy model for datasets."""
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_name = Column(String(255), nullable=False)  # Renamed from id
    full_id = Column(String(255), unique=True, nullable=False)
    project_id = Column(String(255), nullable=False)
    friendly_name = Column(String(255))
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index("ix_datasets_project", "project_id"),
        Index("ix_datasets_name", "dataset_name"),
        Index("ix_datasets_full_id", "full_id"),
    )
    
    @classmethod
    def from_dataclass(cls, dataset: Dataset) -> "DatasetModel":
        """Create a model instance from a dataclass."""
        return cls(
            dataset_name=dataset.id,  # Map id to dataset_name
            full_id=dataset.full_id,
            project_id=dataset.project_id,
            friendly_name=dataset.friendly_name,
            description=dataset.description
        )


class TableModel(Base):
    """SQLAlchemy model for tables."""
    __tablename__ = "tables"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String(255), nullable=False)  # Renamed from id
    full_id = Column(String(255), unique=True, nullable=False)
    dataset_id = Column(String(255), nullable=False)  # No longer a foreign key to datasets.id
    project_id = Column(String(255), nullable=False)
    friendly_name = Column(String(255))
    description = Column(Text)
    table_type = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index("ix_tables_dataset", "dataset_id"),
        Index("ix_tables_project", "project_id"),
        Index("ix_tables_name", "table_name"),
        Index("ix_tables_full_id", "full_id"),
    )
    
    @classmethod
    def from_dataclass(cls, table: Table) -> "TableModel":
        """Create a model instance from a dataclass."""
        return cls(
            table_name=table.id,  # Map id to table_name
            full_id=table.full_id,
            dataset_id=table.dataset_id,
            project_id=table.project_id,
            friendly_name=table.friendly_name,
            description=table.description,
            table_type=table.table_type
        )


class FieldModel(Base):
    """SQLAlchemy model for fields."""
    __tablename__ = "fields"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_id = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    table_id = Column(String(255), nullable=False)  # This is now table_name in TableModel
    dataset_id = Column(String(255), nullable=False)  # This is now dataset_name in DatasetModel
    project_id = Column(String(255), nullable=False)
    field_type = Column(String(50))
    description = Column(Text)
    mode = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index("ix_fields_table", "table_id"),
        Index("ix_fields_dataset", "dataset_id"),
        Index("ix_fields_project", "project_id"),
        Index("ix_fields_name", "name"),
        Index("ix_fields_full_id", "full_id"),
    )
    
    @classmethod
    def from_dataclass(cls, field: Field) -> "FieldModel":
        """Create a model instance from a dataclass."""
        return cls(
            name=field.name,
            full_id=field.full_id,
            table_id=field.table_id,
            dataset_id=field.dataset_id,
            project_id=field.project_id,
            field_type=field.field_type,
            description=field.description,
            mode=field.mode
        )
