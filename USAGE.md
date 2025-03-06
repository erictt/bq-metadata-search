# BigQuery Metadata Search - Usage Guide

This guide explains how to use the BigQuery Metadata Search application.

## Prerequisites

1. Python 3.11 or higher
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
   pip install uv
   uv pip install -e .
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

### Using the Python Module Directly

To extract metadata from a BigQuery project:

```
python -m app.extractor.run --project=your-project-id
```

Full list of parameters:
- `--project` or `-p`: (Required) GCP project ID to extract metadata from
- `--output` or `-o`: (Optional) Save extracted metadata to a JSON file (e.g., `--output=metadata.json`)
- `--no-db`: (Optional) Skip saving to the database
- `--workers` or `-w`: (Optional) Number of worker threads for parallel processing (default: 4)

Example with all options:
```
python -m app.extractor.run --project=your-project-id --output=metadata.json --workers=8
```

### Using the Convenience Script

For easier usage, you can use the provided shell script:

```
./scripts/extract-metadata.sh your-project-id [output-file.json] [workers]
```

Arguments:
1. `PROJECT_ID`: (Required) The Google Cloud project ID to extract metadata from
2. `OUTPUT_FILE`: (Optional) File to save metadata to (e.g., metadata.json)
3. `WORKERS`: (Optional) Number of worker threads for parallel processing (default: 4)

Example:
```
./scripts/extract-metadata.sh my-analytics-project metadata.json 8
```

### Using with Docker

If you're using the Docker setup:

```
docker-compose exec app python -m app.extractor.run --project=your-project-id
```

Or use the convenience script which automatically detects if you're running in Docker:

```
./scripts/extract-metadata.sh your-project-id
```

### Extracting from Multiple Projects

You can extract metadata from multiple projects by running the command for each project:

```
python -m app.extractor.run --project=project-1
python -m app.extractor.run --project=project-2
```

Or with the script:

```
./scripts/extract-metadata.sh project-1
./scripts/extract-metadata.sh project-2
```

The metadata from all projects will be stored in the same database, allowing you to search across all projects.

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
docker-compose exec db psql -U bq_metadata -d bq_metadata
```

Or from your host machine:

```
psql -h localhost -p 5432 -U bq_metadata -d bq_metadata
```

Password: `bq_metadata_password`

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
