#!/bin/bash
# extract-metadata.sh - Extract metadata from a BigQuery project

set -e

if [ $# -eq 0 ]; then
    echo "Usage: ./extract-metadata.sh PROJECT_ID [OUTPUT_FILE] [WORKERS]"
    echo "  PROJECT_ID: The Google Cloud project ID to extract metadata from"
    echo "  OUTPUT_FILE: Optional file to save metadata to (e.g., metadata.json)"
    echo "  WORKERS: Optional number of worker threads for parallel processing (default: 4)"
    exit 1
fi

PROJECT_ID=$1
OUTPUT_PARAM=""
WORKERS_PARAM="--workers=4"  # Default to 4 workers

if [ $# -gt 1 ]; then
    OUTPUT_PARAM="--output=$2"
fi

if [ $# -gt 2 ]; then
    WORKERS_PARAM="--workers=$3"
fi

# Extract worker count from parameter
WORKER_COUNT=${WORKERS_PARAM#--workers=}
echo "Extracting metadata from project: $PROJECT_ID with $WORKER_COUNT worker threads"

# Check if running in Docker
if [ -f "/.dockerenv" ]; then
    # We're inside Docker
    python -m app.extractor.run --project=$PROJECT_ID $OUTPUT_PARAM $WORKERS_PARAM
else
    # We're on the host
    docker-compose exec app python -m app.extractor.run --project=$PROJECT_ID $OUTPUT_PARAM $WORKERS_PARAM
fi

echo "Metadata extraction complete!"
