"""
Tests for the BigQuery metadata extractor.
"""
import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.extractor.bq_client import BigQueryMetadataClient


class TestBigQueryMetadataClient(unittest.TestCase):
    """Tests for the BigQueryMetadataClient class."""
    
    @patch('app.extractor.bq_client.bigquery.Client')
    def test_list_datasets(self, mock_client):
        """Test listing datasets."""
        # Setup mock
        mock_dataset_ref1 = MagicMock()
        mock_dataset_ref1.dataset_id = "dataset1"
        
        mock_dataset_ref2 = MagicMock()
        mock_dataset_ref2.dataset_id = "dataset2"
        
        mock_dataset1 = MagicMock()
        mock_dataset1.dataset_id = "dataset1"
        mock_dataset1.friendly_name = "Dataset 1"
        mock_dataset1.description = "Description 1"
        
        mock_dataset2 = MagicMock()
        mock_dataset2.dataset_id = "dataset2"
        mock_dataset2.friendly_name = "Dataset 2"
        mock_dataset2.description = "Description 2"
        
        mock_client.return_value.list_datasets.return_value = [mock_dataset_ref1, mock_dataset_ref2]
        mock_client.return_value.get_dataset.side_effect = [mock_dataset1, mock_dataset2]
        
        # Execute
        client = BigQueryMetadataClient("test-project")
        datasets = client.list_datasets()
        
        # Verify
        mock_client.return_value.list_datasets.assert_called_once()
        self.assertEqual(len(datasets), 2)
        self.assertEqual(datasets[0]["id"], "dataset1")
        self.assertEqual(datasets[0]["full_id"], "test-project.dataset1")
        self.assertEqual(datasets[0]["friendly_name"], "Dataset 1")
        self.assertEqual(datasets[0]["description"], "Description 1")
    
    @patch('app.extractor.bq_client.bigquery.Client')
    def test_list_tables(self, mock_client):
        """Test listing tables."""
        # Setup mock
        mock_table_ref1 = MagicMock()
        mock_table_ref1.table_id = "table1"
        
        mock_table_ref2 = MagicMock()
        mock_table_ref2.table_id = "table2"
        
        mock_table1 = MagicMock()
        mock_table1.table_id = "table1"
        mock_table1.friendly_name = "Table 1"
        mock_table1.description = "Description 1"
        mock_table1.table_type = "TABLE"
        
        mock_table2 = MagicMock()
        mock_table2.table_id = "table2"
        mock_table2.friendly_name = "Table 2"
        mock_table2.description = "Description 2"
        mock_table2.table_type = "VIEW"
        
        mock_client.return_value.list_tables.return_value = [mock_table_ref1, mock_table_ref2]
        mock_client.return_value.get_table.side_effect = [mock_table1, mock_table2]
        
        # Execute
        client = BigQueryMetadataClient("test-project")
        tables = client.list_tables("dataset1")
        
        # Verify
        mock_client.return_value.list_tables.assert_called_once_with("test-project.dataset1")
        self.assertEqual(len(tables), 2)
        self.assertEqual(tables[0]["id"], "table1")
        self.assertEqual(tables[0]["full_id"], "test-project.dataset1.table1")
        self.assertEqual(tables[0]["friendly_name"], "Table 1")
        self.assertEqual(tables[0]["description"], "Description 1")
        self.assertEqual(tables[0]["table_type"], "TABLE")
    
    @patch('app.extractor.bq_client.bigquery.Client')
    def test_get_table_schema(self, mock_client):
        """Test getting table schema."""
        # Setup mock
        mock_field1 = MagicMock()
        mock_field1.name = "field1"
        mock_field1.field_type = "STRING"
        mock_field1.description = "Description 1"
        mock_field1.mode = "NULLABLE"
        
        mock_field2 = MagicMock()
        mock_field2.name = "field2"
        mock_field2.field_type = "INTEGER"
        mock_field2.description = "Description 2"
        mock_field2.mode = "REQUIRED"
        
        mock_table = MagicMock()
        mock_table.schema = [mock_field1, mock_field2]
        
        mock_client.return_value.get_table.return_value = mock_table
        
        # Execute
        client = BigQueryMetadataClient("test-project")
        fields = client.get_table_schema("dataset1", "table1")
        
        # Verify
        mock_client.return_value.get_table.assert_called_once_with("test-project.dataset1.table1")
        self.assertEqual(len(fields), 2)
        self.assertEqual(fields[0]["name"], "field1")
        self.assertEqual(fields[0]["field_type"], "STRING")
        self.assertEqual(fields[0]["description"], "Description 1")
        self.assertEqual(fields[0]["mode"], "NULLABLE")
        self.assertEqual(fields[0]["full_id"], "test-project.dataset1.table1.field1")


if __name__ == "__main__":
    unittest.main()
