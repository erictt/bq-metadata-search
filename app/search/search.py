"""
Search functionality for BigQuery metadata.
"""
from sqlalchemy import or_, and_
from typing import List, Dict, Any
import logging

from app.storage.db import Database
from app.storage.models import DatasetModel, TableModel, FieldModel

logger = logging.getLogger(__name__)

class MetadataSearch:
    """Search functionality for BigQuery metadata."""
    
    def __init__(self):
        """Initialize the search engine."""
        self.db = Database()
    
    def search(
        self, 
        query: str, 
        project_id: str | None = None,
        entity_type: str | None = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Search for datasets, tables, and fields.
        
        Args:
            query: The search query.
            project_id: Optional project ID to filter by.
            entity_type: Optional entity type to filter by ('dataset', 'table', or 'field').
            
        Returns:
            Dict with datasets, tables, and fields that match the query.
        """
        result = {
            "datasets": [],
            "tables": [],
            "fields": []
        }
        
        # Skip if query is empty
        if not query or len(query.strip()) == 0:
            return result
        
        # Prepare search terms
        search_terms = [f"%{term}%" for term in query.strip().split()]
        
        with self.db.get_session() as session:
            # Search datasets
            if not entity_type or entity_type.lower() == 'dataset':
                dataset_query = session.query(DatasetModel)
                
                if project_id:
                    dataset_query = dataset_query.filter(DatasetModel.project_id == project_id)
                
                for term in search_terms:
                    dataset_query = dataset_query.filter(
                        or_(
                            DatasetModel.id.ilike(term),
                            DatasetModel.friendly_name.ilike(term),
                            DatasetModel.description.ilike(term)
                        )
                    )
                
                datasets = dataset_query.all()
                
                result["datasets"] = [
                    {
                        "id": ds.id,
                        "full_id": ds.full_id,
                        "project_id": ds.project_id,
                        "friendly_name": ds.friendly_name,
                        "description": ds.description
                    }
                    for ds in datasets
                ]
            
            # Search tables
            if not entity_type or entity_type.lower() == 'table':
                table_query = session.query(TableModel)
                
                if project_id:
                    table_query = table_query.filter(TableModel.project_id == project_id)
                
                for term in search_terms:
                    table_query = table_query.filter(
                        or_(
                            TableModel.id.ilike(term),
                            TableModel.friendly_name.ilike(term),
                            TableModel.description.ilike(term)
                        )
                    )
                
                tables = table_query.all()
                
                result["tables"] = [
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
            
            # Search fields
            if not entity_type or entity_type.lower() == 'field':
                field_query = session.query(FieldModel)
                
                if project_id:
                    field_query = field_query.filter(FieldModel.project_id == project_id)
                
                for term in search_terms:
                    field_query = field_query.filter(
                        or_(
                            FieldModel.name.ilike(term),
                            FieldModel.description.ilike(term),
                            FieldModel.field_type.ilike(term)
                        )
                    )
                
                fields = field_query.all()
                
                result["fields"] = [
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
        
        return result

    def advanced_search(
        self,
        terms: Dict[str, str],
        project_id: str | None = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Advanced search with specific filters.
        
        Args:
            terms: Dict mapping field names to search terms.
                Supported fields: name, description, type.
            project_id: Optional project ID to filter by.
            
        Returns:
            Dict with datasets, tables, and fields that match the query.
        """
        result = {
            "datasets": [],
            "tables": [],
            "fields": []
        }
        
        name_term = terms.get("name", "")
        description_term = terms.get("description", "")
        type_term = terms.get("type", "")
        
        with self.db.get_session() as session:
            # Search datasets
            dataset_query = session.query(DatasetModel)
            
            if project_id:
                dataset_query = dataset_query.filter(DatasetModel.project_id == project_id)
            
            conditions = []
            
            if name_term:
                conditions.append(DatasetModel.id.ilike(f"%{name_term}%"))
            
            if description_term:
                conditions.append(DatasetModel.description.ilike(f"%{description_term}%"))
            
            if conditions:
                dataset_query = dataset_query.filter(and_(*conditions))
                datasets = dataset_query.all()
                
                result["datasets"] = [
                    {
                        "id": ds.id,
                        "full_id": ds.full_id,
                        "project_id": ds.project_id,
                        "friendly_name": ds.friendly_name,
                        "description": ds.description
                    }
                    for ds in datasets
                ]
            
            # Search tables
            table_query = session.query(TableModel)
            
            if project_id:
                table_query = table_query.filter(TableModel.project_id == project_id)
            
            conditions = []
            
            if name_term:
                conditions.append(TableModel.id.ilike(f"%{name_term}%"))
            
            if description_term:
                conditions.append(TableModel.description.ilike(f"%{description_term}%"))
            
            if type_term:
                conditions.append(TableModel.table_type.ilike(f"%{type_term}%"))
            
            if conditions:
                table_query = table_query.filter(and_(*conditions))
                tables = table_query.all()
                
                result["tables"] = [
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
            
            # Search fields
            field_query = session.query(FieldModel)
            
            if project_id:
                field_query = field_query.filter(FieldModel.project_id == project_id)
            
            conditions = []
            
            if name_term:
                conditions.append(FieldModel.name.ilike(f"%{name_term}%"))
            
            if description_term:
                conditions.append(FieldModel.description.ilike(f"%{description_term}%"))
            
            if type_term:
                conditions.append(FieldModel.field_type.ilike(f"%{type_term}%"))
            
            if conditions:
                field_query = field_query.filter(and_(*conditions))
                fields = field_query.all()
                
                result["fields"] = [
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
        
        return result
