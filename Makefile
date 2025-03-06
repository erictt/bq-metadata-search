.PHONY: setup run test extract build docker-up docker-down clean

# Setup environment
setup:
	pip install uv
	uv pip install -e .

# Run the application
run:
	uvicorn app.main:app --reload

# Run tests
test:
	pytest

# Run tests with coverage
coverage:
	pytest --cov=app tests/

# Extract metadata from a BigQuery project
extract:
	@read -p "Enter project ID: " project; \
	python -m app.extractor.run --project=$$project

# Build Docker image
build:
	docker build -t bq-lookup .

# Start Docker containers
docker-up:
	docker-compose up -d

# Stop Docker containers
docker-down:
	docker-compose down

# Clean Python cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
