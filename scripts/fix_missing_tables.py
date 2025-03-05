#!/usr/bin/env python
"""
Script to fix database inconsistency by adding tables that exist in the fields table
but are missing from the tables table.
"""
import sys
import os
import logging
from typing import List, Dict, Any, Tuple

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.storage.db import Database
from app.storage.models import Table
from sqlalchemy import text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def get_missing_tables(db: Database) -> List[Tuple[str, str, str]]:
    """
    Find tables that exist in the fields table but not in the tables table.
    
    Returns:
        List of tuples containing (table_id, dataset_id, project_id)
    """
    with db.get_session() as session:
        # Query to find table_id, dataset_id, project_id combinations in fields that don't exist in tables
        query = text("""
            SELECT DISTINCT f.table_id, f.dataset_id, f.project_id
            FROM fields f
            LEFT JOIN tables t ON f.table_id = t.id AND f.dataset_id = t.dataset_id
            WHERE t.id IS NULL
        """)
        
        result = session.execute(query)
        missing_tables = [(row[0], row[1], row[2]) for row in result]
        
        logger.info(f"Found {len(missing_tables)} missing tables")
        return missing_tables

def add_missing_tables(db: Database, missing_tables: List[Tuple[str, str, str]]) -> int:
    """
    Add missing tables to the tables table.
    
    Args:
        db: Database instance
        missing_tables: List of tuples containing (table_id, dataset_id, project_id)
        
    Returns:
        Number of tables added
    """
    count = 0
    
    for table_id, dataset_id, project_id in missing_tables:
        # Create a full_id based on the pattern project_id.dataset_id.table_id
        full_id = f"{project_id}.{dataset_id}.{table_id}"
        
        # Create a new table object
        table = Table(
            id=table_id,
            full_id=full_id,
            dataset_id=dataset_id,
            project_id=project_id,
            friendly_name=table_id,  # Use table_id as friendly_name
            description="Automatically added from fields data",
            table_type="TABLE"  # Assume it's a regular table
        )
        
        try:
            db.save_table(table)
            logger.info(f"Added missing table: {full_id}")
            count += 1
        except Exception as e:
            logger.error(f"Error adding table {full_id}: {e}")
    
    return count

def main():
    """Main function to fix missing tables."""
    logger.info("Starting fix for missing tables")
    
    db = Database()
    
    # Get missing tables
    missing_tables = get_missing_tables(db)
    
    if not missing_tables:
        logger.info("No missing tables found. Database is consistent.")
        return
    
    # Add missing tables
    added_count = add_missing_tables(db, missing_tables)
    
    logger.info(f"Added {added_count} missing tables")
    logger.info("Fix completed")

if __name__ == "__main__":
    main()
