"""
BigQuery client for extracting metadata.
"""

from google.cloud import bigquery
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BigQueryMetadataClient:
    """Client for extracting metadata from BigQuery."""

    def __init__(self, project_id: str):
        """Initialize the BigQuery client.

        Args:
            project_id: The GCP project ID to extract metadata from.
        """
        self.project_id = project_id
        self.client = bigquery.Client(project=project_id)
        logger.info(f"Initialized BigQuery client for project {project_id}")

    def list_datasets(self) -> List[Dict[str, Any]]:
        """List all datasets in the project.

        Returns:
            List of dataset metadata.
        """
        datasets = list(self.client.list_datasets())

        result = []
        for dataset_ref in datasets:
            # Get the full dataset to access all metadata including description
            dataset_id = f"{self.project_id}.{dataset_ref.dataset_id}"
            dataset = self.client.get_dataset(dataset_id)

            result.append(
                {
                    "id": dataset.dataset_id,
                    "full_id": f"{self.project_id}.{dataset.dataset_id}",
                    "friendly_name": dataset.friendly_name,
                    "description": dataset.description or "",  # Handle None description
                }
            )

        logger.info(f"Found {len(result)} datasets in project {self.project_id}")
        logger.info(f"List of datasets: {result}")

        # ignore the dataset ends with '_dev' or '_preprod' or the dataset name matches "data_science"
        datasets = [dataset for dataset in datasets]
        return result

    def list_tables(self, dataset_id: str) -> List[Dict[str, Any]]:
        """List all tables in a dataset.

        Args:
            dataset_id: The dataset ID.

        Returns:
            List of table metadata.
        """
        tables = list(self.client.list_tables(f"{self.project_id}.{dataset_id}"))

        result = []
        for table_ref in tables:
            # Get the full table to access all metadata including description
            table_id = f"{self.project_id}.{dataset_id}.{table_ref.table_id}"
            table = self.client.get_table(table_id)
            result.append(
                {
                    "id": table.table_id,
                    "full_id": f"{self.project_id}.{dataset_id}.{table.table_id}",
                    "friendly_name": table.friendly_name,
                    "description": table.description or "",  # Handle None description
                    "table_type": table.table_type,
                    "dataset_id": dataset_id,
                }
            )

        logger.info(f"Found {len(result)} tables in dataset {dataset_id}")
        return result

    def get_table_schema(self, dataset_id: str, table_id: str) -> List[Dict[str, Any]]:
        """Get the schema of a table.

        Args:
            dataset_id: The dataset ID.
            table_id: The table ID.

        Returns:
            List of field metadata.
        """
        table_ref = f"{self.project_id}.{dataset_id}.{table_id}"
        try:
            table = self.client.get_table(table_ref)

            result = []
            for field in table.schema:
                result.append(
                    {
                        "name": field.name,
                        "field_type": field.field_type,
                        "description": field.description,
                        "mode": field.mode,
                        "table_id": table_id,
                        "dataset_id": dataset_id,
                        "full_id": f"{table_ref}.{field.name}",
                    }
                )

            logger.info(f"Found {len(result)} fields in table {table_ref}")
            return result
        except Exception as e:
            logger.error(f"Error getting schema for table {table_ref}: {e}")
            return []

    def extract_all_metadata(self) -> Dict[str, Any]:
        """Extract all metadata from the project.

        Returns:
            Dict containing datasets, tables, and fields metadata.
        """
        datasets = self.list_datasets()

        tables = []
        fields = []

        for dataset in datasets:
            dataset_tables = self.list_tables(dataset["id"])
            tables.extend(dataset_tables)

            for table in dataset_tables:
                table_fields = self.get_table_schema(dataset["id"], table["id"])
                fields.extend(table_fields)

        return {
            "project_id": self.project_id,
            "datasets": datasets,
            "tables": tables,
            "fields": fields,
        }
