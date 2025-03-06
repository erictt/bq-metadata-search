"""
BigQuery client for extracting metadata.
"""

from google.cloud import bigquery
from typing import List, Dict, Any, Optional
import logging
import concurrent.futures
from functools import partial

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
        # Cache for tables and fields to avoid redundant API calls
        self._table_cache = {}
        logger.info(f"Initialized BigQuery client for project {project_id}")

    def should_skip_dataset(self, dataset_id: str) -> bool:
        """Determine if a dataset should be skipped based on naming patterns.

        Args:
            dataset_id: The dataset ID to check.

        Returns:
            True if the dataset should be skipped, False otherwise.
        """
        # Skip development, pre-production, data science, and log datasets
        # if (
        #     dataset_id.endswith("_dev")
        #     or dataset_id.endswith("_preprd")
        #     or dataset_id.endswith("data_science")
        #     or dataset_id.endswith("log_bq_queries")
        # ):
        #     return True
        # return False

        # if (
        #     (
        #         dataset_id.startswith("cert_")
        #         and (not dataset_id.endswith("_dev"))
        #         and (not dataset_id.endswith("_preprd"))
        #     )
        #     or dataset_id == "conformed_dm"
        #     or dataset_id == "payment_dm"
        #     or dataset_id == "global_finance"
        #     or dataset_id.startswith("paytments_")
        # ):
        #     return False
        # return True
        #

        # if dataset_id.endswith("unified") and (not dataset_id.endswith("p7d_unified")):
        #     return False

        if (
            dataset_id.startswith("salesforce")
            and (not dataset_id.endswith("mirror"))
            and (not dataset_id.endswith("history"))
        ):
            return False
        return True

    def list_datasets(self) -> List[Dict[str, Any]]:
        """List all datasets in the project.

        Returns:
            List of dataset metadata.
        """
        datasets = list(self.client.list_datasets())

        result = []
        for dataset_ref in datasets:
            dataset_name = dataset_ref.dataset_id

            # Skip datasets based on naming patterns
            if self.should_skip_dataset(dataset_name):
                logger.info(f"Skipping dataset {dataset_name} based on naming pattern")
                continue

            # Get the full dataset to access all metadata including description
            dataset_id = f"{self.project_id}.{dataset_name}"
            dataset = self.client.get_dataset(dataset_id)

            result.append(
                {
                    "id": dataset.dataset_id,
                    "full_id": f"{self.project_id}.{dataset.dataset_id}",
                    "friendly_name": dataset.friendly_name,
                    "description": dataset.description or "",  # Handle None description
                }
            )

        logger.info(
            f"Found {len(result)} datasets in project {self.project_id} after filtering"
        )
        return result

    def list_tables(self, dataset_id: str) -> List[Dict[str, Any]]:
        """List all tables in a dataset.

        Args:
            dataset_id: The dataset ID.

        Returns:
            List of table metadata.
        """
        # Get the full dataset reference
        dataset_ref = f"{self.project_id}.{dataset_id}"

        # List all tables in the dataset
        tables = list(self.client.list_tables(dataset_ref))

        # Process tables in batches to reduce API calls
        batch_size = 10  # Adjust based on your needs
        result = []

        for i in range(0, len(tables), batch_size):
            batch = tables[i : i + batch_size]

            for table_ref in batch:
                # Create the full table ID
                full_table_id = f"{dataset_ref}.{table_ref.table_id}"

                # Check if we already have this table in cache
                if full_table_id in self._table_cache:
                    table = self._table_cache[full_table_id]
                else:
                    # Get the full table to access all metadata including description
                    table = self.client.get_table(full_table_id)
                    # Store in cache for future use
                    self._table_cache[full_table_id] = table

                result.append(
                    {
                        "id": table.table_id,
                        "full_id": full_table_id,
                        "friendly_name": table.friendly_name,
                        "description": table.description
                        or "",  # Handle None description
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
            # Check if we already have this table in cache
            if table_ref in self._table_cache:
                table = self._table_cache[table_ref]
            else:
                # Get the full table to access schema
                table = self.client.get_table(table_ref)
                # Store in cache for future use
                self._table_cache[table_ref] = table

            result = []
            for field in table.schema:
                result.append(
                    {
                        "name": field.name,
                        "field_type": field.field_type,
                        "description": field.description
                        or "",  # Handle None description
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

    def _process_table(
        self, dataset_id: str, table: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Process a single table to get its schema.

        This is a helper method for parallel processing.

        Args:
            dataset_id: The dataset ID.
            table: The table metadata.

        Returns:
            List of field metadata.
        """
        return self.get_table_schema(dataset_id, table["id"])

    def extract_metadata_by_dataset(self, max_workers: int = 4):
        """Extract metadata from the project, yielding one dataset at a time.

        This is a generator function that yields metadata for each dataset
        as it's processed, allowing for incremental saving to the database.

        Args:
            max_workers: Maximum number of worker threads for parallel processing.

        Yields:
            Dict containing a single dataset with its tables and fields.
        """
        datasets = self.list_datasets()

        for dataset in datasets:
            dataset_id = dataset["id"]
            dataset_tables = self.list_tables(dataset_id)

            # Process tables in parallel to improve performance
            dataset_fields = []
            if dataset_tables:
                # Create a partial function with the dataset_id already set
                process_table_fn = partial(self._process_table, dataset_id)

                # Use ThreadPoolExecutor for parallel processing
                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=max_workers
                ) as executor:
                    # Submit all table processing tasks
                    future_to_table = {
                        executor.submit(process_table_fn, table): table
                        for table in dataset_tables
                    }

                    # Collect results as they complete
                    for future in concurrent.futures.as_completed(future_to_table):
                        table = future_to_table[future]
                        try:
                            table_fields = future.result()
                            dataset_fields.extend(table_fields)
                            logger.info(
                                f"Processed table {table['id']} with {len(table_fields)} fields"
                            )
                        except Exception as e:
                            logger.error(f"Error processing table {table['id']}: {e}")

            yield {
                "project_id": self.project_id,
                "dataset": dataset,
                "tables": dataset_tables,
                "fields": dataset_fields,
            }
