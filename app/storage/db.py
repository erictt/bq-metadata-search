"""
Database connection and operations.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import NullPool
import logging
import time
from typing import List, Dict, Any

from app.storage.models import (
    Base, Dataset, Table, Field,
    DatasetModel, TableModel, FieldModel
)

logger = logging.getLogger(__name__)

# Get database URL from environment or use SQLite by default
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "sqlite:///./bq_metadata.db"
)

# Configure additional engine arguments based on DB type
engine_args = {}

# For PostgreSQL, we want to disable pooling in some scenarios
if DATABASE_URL.startswith("postgresql"):
    # In standard mode, we want connection pooling
    if os.environ.get("DISABLE_POOL", "0") == "1":
        engine_args["poolclass"] = NullPool

class Database:
    """Database operations for BigQuery metadata."""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one database connection is created."""
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the database connection."""
        self.engine = create_engine(DATABASE_URL, **engine_args)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Try to connect to the database with retries (useful for Docker startup)
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # Create tables if they don't exist
                Base.metadata.create_all(bind=self.engine)
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Database connection attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Failed to connect to database after {max_retries} attempts: {e}")
                    raise
    
    def get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()
    
    def save_dataset(self, dataset: Dataset) -> None:
        """Save a dataset to the database.
        
        Args:
            dataset: The dataset to save.
        """
        db_model = DatasetModel.from_dataclass(dataset)
        
        with self.get_session() as session:
            try:
                existing = session.query(DatasetModel).filter_by(id=dataset.id).first()
                
                if existing:
                    # Update existing record
                    for key, value in vars(db_model).items():
                        if key != '_sa_instance_state' and key != 'id' and value is not None:
                            setattr(existing, key, value)
                else:
                    # Insert new record
                    session.add(db_model)
                
                session.commit()
            except IntegrityError as e:
                logger.error(f"Error saving dataset {dataset.id}: {e}")
                session.rollback()
                raise
    
    def save_table(self, table: Table) -> None:
        """Save a table to the database.
        
        Args:
            table: The table to save.
        """
        db_model = TableModel.from_dataclass(table)
        
        with self.get_session() as session:
            try:
                existing = session.query(TableModel).filter_by(id=table.id).first()
                
                if existing:
                    # Update existing record
                    for key, value in vars(db_model).items():
                        if key != '_sa_instance_state' and key != 'id' and value is not None:
                            setattr(existing, key, value)
                else:
                    # Insert new record
                    session.add(db_model)
                
                session.commit()
            except IntegrityError as e:
                logger.error(f"Error saving table {table.id}: {e}")
                session.rollback()
                raise
    
    def save_field(self, field: Field) -> None:
        """Save a field to the database.
        
        Args:
            field: The field to save.
        """
        db_model = FieldModel.from_dataclass(field)
        
        with self.get_session() as session:
            try:
                existing = session.query(FieldModel).filter_by(full_id=field.full_id).first()
                
                if existing:
                    # Update existing record
                    for key, value in vars(db_model).items():
                        if key != '_sa_instance_state' and key != 'id' and value is not None:
                            setattr(existing, key, value)
                else:
                    # Insert new record
                    session.add(db_model)
                
                session.commit()
            except IntegrityError as e:
                logger.error(f"Error saving field {field.full_id}: {e}")
                session.rollback()
                raise
    
    def get_projects(self) -> List[str]:
        """Get all projects in the database.
        
        Returns:
            List of project IDs.
        """
        with self.get_session() as session:
            projects = session.query(DatasetModel.project_id).distinct().all()
            return [p[0] for p in projects]
    
    def get_datasets(self, project_id: str | None = None) -> List[Dict[str, Any]]:
        """Get all datasets in the database.
        
        Args:
            project_id: Optional project ID to filter by.
            
        Returns:
            List of dataset metadata.
        """
        with self.get_session() as session:
            query = session.query(DatasetModel)
            
            if project_id:
                query = query.filter(DatasetModel.project_id == project_id)
            
            datasets = query.all()
            
            return [
                {
                    "id": ds.id,
                    "full_id": ds.full_id,
                    "project_id": ds.project_id,
                    "friendly_name": ds.friendly_name,
                    "description": ds.description
                }
                for ds in datasets
            ]
    
    def get_tables(
        self, 
        project_id: str | None = None, 
        dataset_id: str | None = None
    ) -> List[Dict[str, Any]]:
        """Get tables from the database.
        
        Args:
            project_id: Optional project ID to filter by.
            dataset_id: Optional dataset ID to filter by.
            
        Returns:
            List of table metadata.
        """
        with self.get_session() as session:
            query = session.query(TableModel)
            
            if project_id:
                query = query.filter(TableModel.project_id == project_id)
            
            if dataset_id:
                query = query.filter(TableModel.dataset_id == dataset_id)
            
            tables = query.all()
            
            return [
                {
                    "id": t.id,
                    "full_id": t.full_id,
                    "dataset_id": t.dataset_id,
                    "project_id": t.project_id,
                    "friendly_name": t.friendly_name,
                    "description": t.description,
                    "table_type": t.table_type
                }
                for t in tables
            ]
    
    def get_fields(
        self,
        project_id: str | None = None,
        dataset_id: str | None = None,
        table_id: str | None = None
    ) -> List[Dict[str, Any]]:
        """Get fields from the database.
        
        Args:
            project_id: Optional project ID to filter by.
            dataset_id: Optional dataset ID to filter by.
            table_id: Optional table ID to filter by.
            
        Returns:
            List of field metadata.
        """
        with self.get_session() as session:
            query = session.query(FieldModel)
            
            if project_id:
                query = query.filter(FieldModel.project_id == project_id)
            
            if dataset_id:
                query = query.filter(FieldModel.dataset_id == dataset_id)
            
            if table_id:
                query = query.filter(FieldModel.table_id == table_id)
            
            fields = query.all()
            
            return [
                {
                    "name": f.name,
                    "full_id": f.full_id,
                    "table_id": f.table_id,
                    "dataset_id": f.dataset_id,
                    "project_id": f.project_id,
                    "field_type": f.field_type,
                    "description": f.description,
                    "mode": f.mode
                }
                for f in fields
            ]
    
    def get_table_with_fields(self, dataset_id: str, table_id: str) -> Dict[str, Any]:
        """Get a table with its fields.
        
        Args:
            dataset_id: The dataset ID.
            table_id: The table ID.
            
        Returns:
            Table metadata with fields.
        """
        with self.get_session() as session:
            table = session.query(TableModel).filter_by(
                dataset_id=dataset_id, 
                id=table_id
            ).first()
            
            if not table:
                return None
            
            fields = session.query(FieldModel).filter_by(
                dataset_id=dataset_id,
                table_id=table_id
            ).all()
            
            return {
                "id": table.id,
                "full_id": table.full_id,
                "dataset_id": table.dataset_id,
                "project_id": table.project_id,
                "friendly_name": table.friendly_name,
                "description": table.description,
                "table_type": table.table_type,
                "fields": [
                    {
                        "name": f.name,
                        "full_id": f.full_id,
                        "field_type": f.field_type,
                        "description": f.description,
                        "mode": f.mode
                    }
                    for f in fields
                ]
            }
