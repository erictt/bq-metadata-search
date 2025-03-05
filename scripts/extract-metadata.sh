#!/bin/bash
# extract-metadata.sh - Extract metadata from a BigQuery project

set -e

if [ $# -eq 0 ]; then
    echo "Usage: ./extract-metadata.sh PROJECT_ID [OUTPUT_FILE]"
    echo "  PROJECT_ID: The Google Cloud project ID to extract metadata from"
    echo "  OUTPUT_FILE: Optional file to save metadata to (e.g., metadata.json)"
    exit 1
fi

PROJECT_ID=$1
OUTPUT_PARAM=""

if [ $# -gt 1 ]; then
    OUTPUT_PARAM="--output=$2"
fi

echo "Extracting metadata from project: $PROJECT_ID"

# Check if running in Docker
if [ -f "/.dockerenv" ]; then
    # We're inside Docker
    python -m app.extractor.run --project=$PROJECT_ID $OUTPUT_PARAM
else
    # We're on the host
    docker-compose exec app python -m app.extractor.run --project=$PROJECT_ID $OUTPUT_PARAM
fi

echo "Metadata extraction complete!"
