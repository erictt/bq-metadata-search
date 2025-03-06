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

def run_extraction(project_id: str, output_file: str = None, save_to_db: bool = True, workers: int = 4):
    """Run the extraction process.
    
    Args:
        project_id: The GCP project ID to extract metadata from.
        output_file: Optional file to save the extracted metadata to.
        save_to_db: Whether to save the metadata to the database.
        workers: Number of worker threads for parallel processing.
    """
    client = BigQueryMetadataClient(project_id)
    logger.info(f"Starting extraction for project {project_id} with {workers} worker threads")
    
    # Initialize counters
    total_datasets = 0
    total_tables = 0
    total_fields = 0
    
    # Initialize output data structure if we need to save to a file
    if output_file:
        all_metadata = {
            "project_id": project_id,
            "datasets": [],
            "tables": [],
            "fields": []
        }
    
    # Process datasets incrementally
    if save_to_db:
        db = Database()
    
    # Extract and process one dataset at a time
    for dataset_metadata in client.extract_metadata_by_dataset(max_workers=workers):
        dataset_data = dataset_metadata["dataset"]
        tables_data = dataset_metadata["tables"]
        fields_data = dataset_metadata["fields"]
        
        # Update counters
        total_datasets += 1
        total_tables += len(tables_data)
        total_fields += len(fields_data)
        
        # Save to output file if needed
        if output_file:
            all_metadata["datasets"].append(dataset_data)
            all_metadata["tables"].extend(tables_data)
            all_metadata["fields"].extend(fields_data)
        
        # Save to database if needed
        if save_to_db:
            # Save dataset
            dataset = Dataset(
                id=dataset_data["id"],
                full_id=dataset_data["full_id"],
                friendly_name=dataset_data["friendly_name"],
                description=dataset_data["description"],
                project_id=project_id
            )
            db.save_dataset(dataset)
            
            # Save tables
            for table_data in tables_data:
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
            for field_data in fields_data:
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
            
            logger.info(f"Saved dataset {dataset_data['id']} with {len(tables_data)} tables and {len(fields_data)} fields to database")
    
    # Write to output file if needed
    if output_file:
        with open(output_file, "w") as f:
            json.dump(all_metadata, f, indent=2)
        logger.info(f"Saved metadata to {output_file}")
    
    logger.info(f"Extraction complete. Processed {total_datasets} datasets, "
                f"{total_tables} tables, {total_fields} fields")

def main():
    parser = argparse.ArgumentParser(description="Extract metadata from BigQuery")
    parser.add_argument("--project", "-p", required=True, help="GCP project ID")
    parser.add_argument("--output", "-o", help="Output file for JSON metadata")
    parser.add_argument("--no-db", action="store_true", help="Don't save to database")
    parser.add_argument("--workers", "-w", type=int, default=4, 
                        help="Number of worker threads for parallel processing (default: 4)")
    
    args = parser.parse_args()
    
    run_extraction(
        project_id=args.project,
        output_file=args.output,
        save_to_db=not args.no_db,
        workers=args.workers
    )

if __name__ == "__main__":
    main()
