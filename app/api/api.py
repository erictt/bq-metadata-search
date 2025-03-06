"""
API endpoints for BigQuery metadata.
"""

from fastapi import APIRouter, Query, Path, HTTPException, status
from typing import List, Dict, Any, Annotated
from pydantic import BaseModel, Field

from app.storage.db import Database
from app.search.search import MetadataSearch

api_router = APIRouter()
db = Database()
search_engine = MetadataSearch()


class SearchQuery(BaseModel):
    """Search query model."""

    query: str
    project_id: str | None = None
    entity_type: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "user",
                    "project_id": "my-project",
                    "entity_type": "table"
                }
            ]
        }
    }


class AdvancedSearchQuery(BaseModel):
    """Advanced search query model."""

    name: str | None = None
    description: str | None = None
    type: str | None = None
    project_id: str | None = None
    dataset_id: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "user",
                    "description": "customer",
                    "type": "table",
                    "project_id": "my-project",
                    "dataset_id": "my-dataset"
                }
            ]
        }
    }


@api_router.get("/projects", response_model=List[str])
async def get_projects():
    """Get all projects."""
    return db.get_projects()


@api_router.get("/datasets", response_model=List[Dict[str, Any]])
async def get_datasets(
    project_id: Annotated[str | None, Query(description="Optional project ID to filter by")] = None
):
    """Get datasets.

    Args:
        project_id: Optional project ID to filter by.
    """
    return db.get_datasets(project_id=project_id)


@api_router.get("/tables", response_model=List[Dict[str, Any]])
async def get_tables(
    project_id: Annotated[str | None, Query(description="Optional project ID to filter by")] = None,
    dataset_id: Annotated[str | None, Query(description="Optional dataset ID to filter by")] = None,
):
    """Get tables.

    Args:
        project_id: Optional project ID to filter by.
        dataset_id: Optional dataset ID to filter by.
    """
    return db.get_tables(project_id=project_id, dataset_id=dataset_id)


@api_router.get("/fields", response_model=List[Dict[str, Any]])
async def get_fields(
    project_id: Annotated[str | None, Query(description="Optional project ID to filter by")] = None,
    dataset_id: Annotated[str | None, Query(description="Optional dataset ID to filter by")] = None,
    table_id: Annotated[str | None, Query(description="Optional table ID to filter by")] = None,
):
    """Get fields.

    Args:
        project_id: Optional project ID to filter by.
        dataset_id: Optional dataset ID to filter by.
        table_id: Optional table ID to filter by.
    """
    return db.get_fields(
        project_id=project_id, dataset_id=dataset_id, table_id=table_id
    )


@api_router.get("/tables/{dataset_id}/{table_id}", response_model=Dict[str, Any])
async def get_table_with_fields(
    dataset_id: Annotated[str, Path(description="Dataset ID")],
    table_id: Annotated[str, Path(description="Table ID")],
):
    """Get a table with its fields.

    Args:
        dataset_id: Dataset ID.
        table_id: Table ID.
    """
    table = db.get_table_with_fields(dataset_id=dataset_id, table_id=table_id)

    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    return table


@api_router.post("/search", response_model=Dict[str, List[Dict[str, Any]]])
async def search(query: SearchQuery):
    """Search for datasets, tables, and fields.

    Args:
        query: Search query.
    """
    return search_engine.search(
        query=query.query, project_id=query.project_id, entity_type=query.entity_type
    )


@api_router.post("/advanced-search", response_model=Dict[str, List[Dict[str, Any]]])
async def advanced_search(query: AdvancedSearchQuery):
    """Advanced search with specific filters.

    Args:
        query: Advanced search query.
    """
    terms = {
        "name": query.name or "",
        "description": query.description or "",
        "type": query.type or "",
    }

    return search_engine.advanced_search(
        terms=terms, 
        project_id=query.project_id,
        dataset_id=query.dataset_id
    )


@api_router.delete("/datasets/{project_id}/{dataset_id}")
async def delete_dataset(
    project_id: Annotated[str, Path(description="Project ID")],
    dataset_id: Annotated[str, Path(description="Dataset ID")],
):
    """Delete a dataset and all its associated tables and fields.

    Args:
        project_id: Project ID.
        dataset_id: Dataset ID.
    """
    success = db.delete_dataset(dataset_id=dataset_id, project_id=project_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Dataset {dataset_id} not found in project {project_id}"
        )
    
    return {"message": f"Dataset {dataset_id} deleted successfully"}


@api_router.delete("/tables/{project_id}/{dataset_id}/{table_id}")
async def delete_table(
    project_id: Annotated[str, Path(description="Project ID")],
    dataset_id: Annotated[str, Path(description="Dataset ID")],
    table_id: Annotated[str, Path(description="Table ID")],
):
    """Delete a table and all its associated fields.

    Args:
        project_id: Project ID.
        dataset_id: Dataset ID.
        table_id: Table ID.
    """
    success = db.delete_table(
        dataset_id=dataset_id, 
        table_id=table_id, 
        project_id=project_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Table {table_id} not found in dataset {dataset_id}"
        )
    
    return {"message": f"Table {table_id} deleted successfully"}
