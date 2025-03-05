"""
Tests for the search functionality.
"""
import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.search.search import MetadataSearch
from app.storage.models import DatasetModel, TableModel, FieldModel


class TestMetadataSearch(unittest.TestCase):
    """Tests for the MetadataSearch class."""
    
    @patch('app.search.search.Database')
    def test_search_empty_query(self, mock_db):
        """Test searching with an empty query."""
        # Setup
        search = MetadataSearch()
        
        # Execute
        result = search.search("")
        
        # Verify
        self.assertEqual(result, {"datasets": [], "tables": [], "fields": []})
        mock_db.return_value.get_session.assert_not_called()
    
    @patch('app.search.search.Database')
    def test_search_datasets(self, mock_db):
        """Test searching for datasets."""
        # Setup mock
        mock_session = MagicMock()
        mock_db.return_value.get_session.return_value.__enter__.return_value = mock_session
        
        mock_dataset1 = MagicMock(spec=DatasetModel)
        mock_dataset1.id = "dataset1"
        mock_dataset1.full_id = "project1.dataset1"
        mock_dataset1.project_id = "project1"
        mock_dataset1.friendly_name = "Dataset 1"
        mock_dataset1.description = "Description 1"
        
        mock_dataset2 = MagicMock(spec=DatasetModel)
        mock_dataset2.id = "dataset2"
        mock_dataset2.full_id = "project1.dataset2"
        mock_dataset2.project_id = "project1"
        mock_dataset2.friendly_name = "Dataset 2"
        mock_dataset2.description = "Description 2"
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_dataset1, mock_dataset2]
        
        mock_session.query.return_value = mock_query
        
        # Execute
        search = MetadataSearch()
        result = search.search("test", entity_type="dataset")
        
        # Verify
        self.assertEqual(len(result["datasets"]), 2)
        self.assertEqual(result["datasets"][0]["id"], "dataset1")
        self.assertEqual(result["datasets"][0]["full_id"], "project1.dataset1")
        self.assertEqual(result["datasets"][0]["project_id"], "project1")
        self.assertEqual(result["datasets"][0]["friendly_name"], "Dataset 1")
        self.assertEqual(result["datasets"][0]["description"], "Description 1")
        
        self.assertEqual(len(result["tables"]), 0)
        self.assertEqual(len(result["fields"]), 0)
    
    @patch('app.search.search.Database')
    def test_advanced_search(self, mock_db):
        """Test advanced search."""
        # Setup mock
        mock_session = MagicMock()
        mock_db.return_value.get_session.return_value.__enter__.return_value = mock_session
        
        mock_field1 = MagicMock(spec=FieldModel)
        mock_field1.name = "field1"
        mock_field1.full_id = "project1.dataset1.table1.field1"
        mock_field1.table_id = "table1"
        mock_field1.dataset_id = "dataset1"
        mock_field1.project_id = "project1"
        mock_field1.field_type = "STRING"
        mock_field1.description = "Description 1"
        mock_field1.mode = "NULLABLE"
        mock_field1.friendly_name = "Field 1"
        mock_field1.table_type = "TABLE"
        
        mock_field2 = MagicMock(spec=FieldModel)
        mock_field2.name = "field2"
        mock_field2.full_id = "project1.dataset1.table1.field2"
        mock_field2.table_id = "table1"
        mock_field2.dataset_id = "dataset1"
        mock_field2.project_id = "project1"
        mock_field2.field_type = "INTEGER"
        mock_field2.description = "Description 2"
        mock_field2.mode = "REQUIRED"
        mock_field2.friendly_name = "Field 2"
        mock_field2.table_type = "TABLE"
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_field1, mock_field2]
        
        mock_session.query.return_value = mock_query
        
        # Execute
        search = MetadataSearch()
        result = search.advanced_search({"name": "field", "type": "STRING"})
        
        # Verify
        self.assertEqual(len(result["fields"]), 2)
        self.assertEqual(result["fields"][0]["name"], "field1")
        self.assertEqual(result["fields"][0]["field_type"], "STRING")
        self.assertEqual(result["fields"][0]["description"], "Description 1")
        self.assertEqual(result["fields"][0]["mode"], "NULLABLE")
        
    @patch('app.search.search.Database')
    def test_advanced_search_with_dataset(self, mock_db):
        """Test advanced search with dataset filter."""
        # Setup mock
        mock_session = MagicMock()
        mock_db.return_value.get_session.return_value.__enter__.return_value = mock_session
        
        mock_table1 = MagicMock(spec=TableModel)
        mock_table1.id = "table1"
        mock_table1.full_id = "project1.dataset1.table1"
        mock_table1.dataset_id = "dataset1"
        mock_table1.project_id = "project1"
        mock_table1.friendly_name = "Table 1"
        mock_table1.description = "Description 1"
        mock_table1.table_type = "TABLE"
        mock_table1.name = "table1"
        mock_table1.table_id = "table1"
        mock_table1.field_type = "STRING"
        mock_table1.mode = "NULLABLE"  # Add this attribute
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_table1]
        
        mock_session.query.return_value = mock_query
        
        # Execute
        search = MetadataSearch()
        result = search.advanced_search(
            {"name": "table"},
            project_id="project1",
            dataset_id="dataset1"
        )
        
        # Verify
        self.assertEqual(len(result["tables"]), 1)
        self.assertEqual(result["tables"][0]["id"], "table1")
        self.assertEqual(result["tables"][0]["dataset_id"], "dataset1")
        self.assertEqual(result["tables"][0]["project_id"], "project1")


if __name__ == "__main__":
    unittest.main()
