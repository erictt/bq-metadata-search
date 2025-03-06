FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PostgreSQL
RUN apt-get update && apt-get install -y \
  gcc \
  libpq-dev \
  postgresql-client \
  && rm -rf /var/lib/apt/lists/*

# Install uv and dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir uv && \
    uv pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV DATABASE_URL=postgresql://bq_metadata:bq_metadata_password@db:5432/bq_metadata

# Wait for PostgreSQL to be ready before starting the app
COPY scripts/wait-for-db.sh /wait-for-db.sh
RUN chmod +x /wait-for-db.sh

# Run the application
# CMD ["/wait-for-db.sh", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
