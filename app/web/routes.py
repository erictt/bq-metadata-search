"""
Web routes for BigQuery metadata UI.
"""

from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated
import os

from app.storage.db import Database
from app.search.search import MetadataSearch

# Create templates directory if it doesn't exist
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(templates_dir, exist_ok=True)

templates = Jinja2Templates(directory=templates_dir)
web_router = APIRouter()
db = Database()
search_engine = MetadataSearch()


@web_router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Homepage."""
    projects = db.get_projects()

    return templates.TemplateResponse(
        "index.html", {"request": request, "projects": projects}
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


@web_router.get("/advanced-search", response_class=HTMLResponse)
async def advanced_search_page(request: Request):
    """Advanced search page."""
    projects = db.get_projects()

    return templates.TemplateResponse(
        "advanced_search.html",
        {"request": request, "projects": projects, "results": {}},
    )


@web_router.post("/advanced-search", response_class=HTMLResponse)
async def advanced_search_results(
    request: Request,
    name: Annotated[str | None, Form(description="Name to search for")] = None,
    description: Annotated[str | None, Form(description="Description to search for")] = None,
    type: Annotated[str | None, Form(description="Type to filter by")] = None,
    project_id: Annotated[str | None, Form(description="Project ID to filter by")] = None,
):
    """Advanced search results."""
    projects = db.get_projects()

    terms = {"name": name or "", "description": description or "", "type": type or ""}

    results = search_engine.advanced_search(terms=terms, project_id=project_id)

    return templates.TemplateResponse(
        "advanced_search.html",
        {
            "request": request,
            "projects": projects,
            "name": name,
            "description": description,
            "type": type,
            "project_id": project_id,
            "results": results,
        },
    )
