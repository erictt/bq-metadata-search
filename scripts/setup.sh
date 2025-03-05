#!/bin/bash
# setup.sh - Initialize the BigQuery Metadata Search application

set -e

echo "Setting up BigQuery Metadata Search..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker and Docker Compose before continuing."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose before continuing."
    exit 1
fi

# Create the credentials directory
mkdir -p credentials
echo "Created credentials directory"

# Check if credentials file exists
if [ ! -f "credentials/service-account-key.json" ]; then
    echo "WARNING: Google Cloud service account key not found."
    echo "Please copy your service account key to: $(pwd)/credentials/service-account-key.json"
    echo ""
fi

# Build and start the containers
echo "Building and starting Docker containers..."
docker-compose up -d --build

echo ""
echo "Setup complete! The application is now running at http://localhost:8000"
echo ""
echo "Next steps:"
echo "1. Ensure your Google Cloud credentials are in ./credentials/service-account-key.json"
echo "2. Extract metadata from your BigQuery project:"
echo "   docker-compose exec app python -m app.extractor.run --project=your-project-id"
echo "3. Access the web interface at http://localhost:8000"
echo ""
echo "For more information, see the USAGE.md file."
