"""
Main application entry point for BigQuery Metadata Search.
"""

import uvicorn
import sys
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.api import api_router
from app.web.routes import web_router

app = FastAPI(
    title="BigQuery Metadata Search",
    description="Search and browse BigQuery metadata",
    version="1.0.0",
    openapi_tags=[
        {"name": "api", "description": "API endpoints for metadata"},
        {"name": "web", "description": "Web UI routes"},
    ],
)

# API routes
app.include_router(api_router, prefix="/api")

# Web UI routes
app.include_router(web_router)

# Mount static files
app.mount("/static", StaticFiles(directory="app/web/static"), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
