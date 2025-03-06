#!/usr/bin/env python
"""
Script to test the database connection and query the datasets table.
"""
import sys
import os
import logging

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.storage.db import Database
from app.storage.models import DatasetModel, TableModel, FieldModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def test_connection():
    """Test the database connection and query the datasets table."""
    db = Database()
    
    with db.get_session() as session:
        try:
            # Query the datasets table
            datasets = session.query(DatasetModel).all()
            logger.info(f"Found {len(datasets)} datasets")
            
            # Print the first dataset
            if datasets:
                dataset = datasets[0]
                logger.info(f"First dataset: id={dataset.id}, dataset_name={dataset.dataset_name}, full_id={dataset.full_id}")
            
            # Query the tables table
            tables = session.query(TableModel).all()
            logger.info(f"Found {len(tables)} tables")
            
            # Print the first table
            if tables:
                table = tables[0]
                logger.info(f"First table: id={table.id}, table_name={table.table_name}, full_id={table.full_id}")
            
            # Query the fields table
            fields = session.query(FieldModel).all()
            logger.info(f"Found {len(fields)} fields")
            
            # Print the first field
            if fields:
                field = fields[0]
                logger.info(f"First field: id={field.id}, name={field.name}, full_id={field.full_id}")
            
            logger.info("Database connection and queries successful")
            
        except Exception as e:
            logger.error(f"Error querying database: {e}")
            raise

if __name__ == "__main__":
    test_connection()
