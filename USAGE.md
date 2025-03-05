# BigQuery Metadata Search - Usage Guide

This guide explains how to use the BigQuery Metadata Search application.

## Prerequisites

1. Python 3.7 or higher
2. Google Cloud SDK installed and configured
3. Access to BigQuery projects you want to extract metadata from
4. PostgreSQL (if using the Docker setup) or SQLite (for local development)

## Setup

1. Clone the repository:
   ```
   git clone https://your-repository-url/bq-lookup.git
   cd bq-lookup
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up Google Cloud credentials:
   ```
   gcloud auth application-default login
   ```

   Or set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to your service account key file:
   ```
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   ```

## Database Configuration

The application supports both SQLite and PostgreSQL databases:

### SQLite (Default for local development)

No additional configuration is needed. The database will be created at `./bq_metadata.db`.

### PostgreSQL

To use PostgreSQL, set the `DATABASE_URL` environment variable:

```
export DATABASE_URL=postgresql://username:password@localhost:5432/dbname
```

## Extracting Metadata

To extract metadata from a BigQuery project:

```
python -m app.extractor.run --project=your-project-id
```

Optional parameters:
- `--output=output.json`: Save extracted metadata to a JSON file
- `--no-db`: Skip saving to the database

You can extract metadata from multiple projects by running the command for each project.

## Running the Application

Start the web application:

```
uvicorn app.main:app --reload
```

The application will be available at http://localhost:8000

## Using Docker

The Docker setup includes both the application and a PostgreSQL database:

1. Build and start the containers:
   ```
   docker-compose up -d
   ```

2. Add your Google Cloud credentials:
   ```
   mkdir -p credentials
   cp /path/to/service-account-key.json ./credentials/
   ```

3. Extract metadata (from inside the container):
   ```
   docker-compose exec app python -m app.extractor.run --project=your-project-id
   ```

The application will be available at http://localhost:8000

### Accessing the PostgreSQL Database

You can connect to the PostgreSQL database using:

```
docker-compose exec db psql -U bqlookup -d bqlookup
```

Or from your host machine:

```
psql -h localhost -p 5432 -U bqlookup -d bqlookup
```

Password: `bqlookup_password`

## Using the Web Interface

The web interface provides several ways to explore and search the metadata:

### Home Page

- Lists all projects in the database
- Provides quick links to search and advanced search

### Project View

- Shows all datasets in a project
- Click on a dataset to view its tables

### Dataset View

- Shows all tables in a dataset
- Click on a table to view its schema

### Table View

- Shows detailed information about a table
- Lists all fields with their types, modes, and descriptions

### Search

- Simple search across all metadata
- Filter by project if needed
- Results are grouped by datasets, tables, and fields

### Advanced Search

- Search by specific criteria:
  - Name: Search in dataset/table/field names
  - Description: Search in descriptions
  - Type: Search by table type or field type
  - Project: Filter by specific project

## Using the API

The application also provides a REST API:

### Endpoints

- `GET /api/projects`: List all projects
- `GET /api/datasets?project_id=X`: List datasets (optionally filter by project)
- `GET /api/tables?project_id=X&dataset_id=Y`: List tables (optionally filter by project and dataset)
- `GET /api/fields?project_id=X&dataset_id=Y&table_id=Z`: List fields (optionally filter by project, dataset, and table)
- `GET /api/tables/{dataset_id}/{table_id}`: Get table details with fields
- `POST /api/search`: Search for metadata
  - Request body: `{"query": "search term", "project_id": "optional", "entity_type": "optional"}`
- `POST /api/advanced-search`: Advanced search
  - Request body: `{"name": "optional", "description": "optional", "type": "optional", "project_id": "optional"}`

### Example API Usage

Search for metadata with curl:

```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "user", "project_id": "my-project"}'
```

Get table details:

```bash
curl "http://localhost:8000/api/tables/my_dataset/my_table"
```
