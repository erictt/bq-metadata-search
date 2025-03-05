"""
Script to run the BigQuery metadata extractor.
"""
import argparse
import logging
import json
import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.extractor.bq_client import BigQueryMetadataClient
from app.storage.db import Database
from app.storage.models import Dataset, Table, Field

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def run_extraction(project_id: str, output_file: str = None, save_to_db: bool = True):
    """Run the extraction process.
    
    Args:
        project_id: The GCP project ID to extract metadata from.
        output_file: Optional file to save the extracted metadata to.
        save_to_db: Whether to save the metadata to the database.
    """
    client = BigQueryMetadataClient(project_id)
    logger.info(f"Starting extraction for project {project_id}")
    
    metadata = client.extract_all_metadata()
    logger.info(f"Extracted {len(metadata['datasets'])} datasets, "
                f"{len(metadata['tables'])} tables, "
                f"{len(metadata['fields'])} fields")
    
    if output_file:
        with open(output_file, "w") as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Saved metadata to {output_file}")
    
    if save_to_db:
        db = Database()
        
        # Save datasets
        for dataset_data in metadata["datasets"]:
            dataset = Dataset(
                id=dataset_data["id"],
                full_id=dataset_data["full_id"],
                friendly_name=dataset_data["friendly_name"],
                description=dataset_data["description"],
                project_id=project_id
            )
            db.save_dataset(dataset)
        
        # Save tables
        for table_data in metadata["tables"]:
            table = Table(
                id=table_data["id"],
                full_id=table_data["full_id"],
                friendly_name=table_data["friendly_name"],
                description=table_data["description"],
                table_type=table_data["table_type"],
                dataset_id=table_data["dataset_id"],
                project_id=project_id
            )
            db.save_table(table)
        
        # Save fields
        for field_data in metadata["fields"]:
            field = Field(
                name=field_data["name"],
                field_type=field_data["field_type"],
                description=field_data["description"],
                mode=field_data["mode"],
                table_id=field_data["table_id"],
                dataset_id=field_data["dataset_id"],
                full_id=field_data["full_id"],
                project_id=project_id
            )
            db.save_field(field)
        
        logger.info("Saved metadata to database")

def main():
    parser = argparse.ArgumentParser(description="Extract metadata from BigQuery")
    parser.add_argument("--project", "-p", required=True, help="GCP project ID")
    parser.add_argument("--output", "-o", help="Output file for JSON metadata")
    parser.add_argument("--no-db", action="store_true", help="Don't save to database")
    
    args = parser.parse_args()
    
    run_extraction(
        project_id=args.project,
        output_file=args.output,
        save_to_db=not args.no_db
    )

if __name__ == "__main__":
    main()
