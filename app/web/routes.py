"""
Web routes for BigQuery metadata UI.
"""

from fastapi import APIRouter, Request, Form, Query, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated
import os
import logging

from app.storage.db import Database
from app.search.search import MetadataSearch

logger = logging.getLogger(__name__)

# Create templates directory if it doesn't exist
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(templates_dir, exist_ok=True)

templates = Jinja2Templates(directory=templates_dir)
web_router = APIRouter()
db = Database()
search_engine = MetadataSearch()


@web_router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    # Common parameters
    project_id: Annotated[str | None, Query(description="Project ID to filter by")] = None,
    dataset_id: Annotated[str | None, Query(description="Dataset ID to filter by")] = None,
    # Search mode
    search_mode: Annotated[str | None, Query(description="Search mode (fuzzy or field)")] = None,
    # Fuzzy search parameters
    q: Annotated[str | None, Query(description="Search query for fuzzy search")] = None,
    # Field-specific search parameters
    name: Annotated[str | None, Query(description="Name to search for")] = None,
    description: Annotated[str | None, Query(description="Description to search for")] = None,
    type: Annotated[str | None, Query(description="Type to filter by")] = None,
):
    """Homepage with integrated search functionality."""
    projects = db.get_projects()
    datasets = []
    results = {}
    search_performed = False
    
    # Get datasets for the project if specified
    if project_id:
        datasets = db.get_datasets(project_id=project_id)
    
    # Handle fuzzy search mode
    if search_mode == "fuzzy" and q:
        results = search_engine.search(query=q, project_id=project_id)
        search_performed = True
    
    # Handle field-specific search mode
    elif search_mode == "field" and (name or description or type):
        terms = {"name": name or "", "description": description or "", "type": type or ""}
        results = search_engine.advanced_search(
            terms=terms, 
            project_id=project_id,
            dataset_id=dataset_id
        )
        search_performed = True
    
    # For backward compatibility or direct access without search_mode
    elif q:
        # If we have a general query but no mode, default to fuzzy search
        results = search_engine.search(query=q, project_id=project_id)
        search_performed = True
    elif name or description or type:
        # If we have field parameters but no mode, default to field search
        terms = {"name": name or "", "description": description or "", "type": type or ""}
        results = search_engine.advanced_search(
            terms=terms, 
            project_id=project_id,
            dataset_id=dataset_id
        )
        search_performed = True

    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "projects": projects,
            "datasets": datasets,
            "query": q,
            "project_id": project_id,
            "name": name,
            "description": description,
            "type": type,
            "dataset_id": dataset_id,
            "search_mode": search_mode,
            "results": results,
            "search_performed": search_performed
        }
    )


@web_router.get("/project/{project_id}", response_class=HTMLResponse)
async def project_details(request: Request, project_id: str):
    """Project details page."""
    datasets = db.get_datasets(project_id=project_id)

    return templates.TemplateResponse(
        "project.html",
        {"request": request, "project_id": project_id, "datasets": datasets},
    )


@web_router.get("/dataset/{project_id}/{dataset_id}", response_class=HTMLResponse)
async def dataset_details(request: Request, project_id: str, dataset_id: str):
    """Dataset details page."""
    tables = db.get_tables(project_id=project_id, dataset_id=dataset_id)

    return templates.TemplateResponse(
        "dataset.html",
        {
            "request": request,
            "project_id": project_id,
            "dataset_id": dataset_id,
            "tables": tables,
        },
    )


@web_router.post("/dataset/{project_id}/{dataset_id}/delete")
async def delete_dataset(project_id: str, dataset_id: str):
    """Delete a dataset and all its associated tables and fields."""
    success = db.delete_dataset(dataset_id=dataset_id, project_id=project_id)
    
    if not success:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"Dataset {dataset_id} not found in project {project_id}"}
        )
    
    # Redirect to the project page
    return RedirectResponse(
        url=f"/project/{project_id}", 
        status_code=status.HTTP_303_SEE_OTHER
    )


@web_router.get(
    "/table/{project_id}/{dataset_id}/{table_id}", response_class=HTMLResponse
)
async def table_details(
    request: Request, project_id: str, dataset_id: str, table_id: str
):
    """Table details page."""
    table = db.get_table_with_fields(dataset_id=dataset_id, table_id=table_id)

    return templates.TemplateResponse(
        "table.html",
        {
            "request": request,
            "project_id": project_id,
            "dataset_id": dataset_id,
            "table_id": table_id,
            "table": table,
        },
    )


@web_router.post("/table/{project_id}/{dataset_id}/{table_id}/delete")
async def delete_table(project_id: str, dataset_id: str, table_id: str):
    """Delete a table and all its associated fields."""
    success = db.delete_table(
        dataset_id=dataset_id, 
        table_id=table_id, 
        project_id=project_id
    )
    
    if not success:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"Table {table_id} not found in dataset {dataset_id}"}
        )
    
    # Redirect to the dataset page
    return RedirectResponse(
        url=f"/dataset/{project_id}/{dataset_id}", 
        status_code=status.HTTP_303_SEE_OTHER
    )


@web_router.get("/search", response_class=HTMLResponse)
async def search_page(
    request: Request,
    q: Annotated[str | None, Query(description="Search query")] = None,
    project_id: Annotated[str | None, Query(description="Project ID to filter by")] = None,
):
    """Search page."""
    results = {}
    projects = db.get_projects()

    if q:
        results = search_engine.search(query=q, project_id=project_id)

    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "query": q,
            "project_id": project_id,
            "projects": projects,
            "results": results,
        },
    )


@web_router.get("/datasets")
async def get_datasets(project_id: str | None = None):
    """Get datasets for a project as JSON."""
    if not project_id:
        return JSONResponse(content=[])
    
    datasets = db.get_datasets(project_id=project_id)
    # Log the datasets for debugging
    logger.info(f"Fetched datasets for project {project_id}: {datasets}")
    return JSONResponse(content=datasets)


@web_router.get("/advanced-search", response_class=HTMLResponse)
async def advanced_search_page(request: Request):
    """Advanced search page."""
    projects = db.get_projects()
    datasets = []  # Empty list initially, will be populated via JavaScript

    return templates.TemplateResponse(
        "advanced_search.html",
        {
            "request": request, 
            "projects": projects, 
            "datasets": datasets,
            "results": {}
        },
    )


@web_router.post("/advanced-search", response_class=HTMLResponse)
async def advanced_search_results(
    request: Request,
    name: Annotated[str | None, Form(description="Name to search for")] = None,
    description: Annotated[str | None, Form(description="Description to search for")] = None,
    type: Annotated[str | None, Form(description="Type to filter by")] = None,
    project_id: Annotated[str | None, Form(description="Project ID to filter by")] = None,
    dataset_id: Annotated[str | None, Form(description="Dataset ID to filter by")] = None,
):
    """Advanced search results."""
    projects = db.get_projects()
    datasets = []
    
    if project_id:
        datasets = db.get_datasets(project_id=project_id)

    terms = {"name": name or "", "description": description or "", "type": type or ""}

    results = search_engine.advanced_search(
        terms=terms, 
        project_id=project_id,
        dataset_id=dataset_id
    )

    return templates.TemplateResponse(
        "advanced_search.html",
        {
            "request": request,
            "projects": projects,
            "datasets": datasets,
            "name": name,
            "description": description,
            "type": type,
            "project_id": project_id,
            "dataset_id": dataset_id,
            "results": results,
        },
    )
