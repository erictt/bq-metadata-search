-- Initialization script for PostgreSQL

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create extension for full-text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create indexes for search optimization after tables are created by SQLAlchemy
CREATE OR REPLACE FUNCTION create_search_indexes() RETURNS void AS $$
BEGIN
    -- Check if tables exist before creating indexes
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'datasets') THEN
        -- Create GIN indexes for full-text search on datasets
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_datasets_description_trgm') THEN
            CREATE INDEX idx_datasets_description_trgm ON datasets USING GIN (description gin_trgm_ops);
        END IF;
    END IF;

    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'tables') THEN
        -- Create GIN indexes for full-text search on tables
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_tables_description_trgm') THEN
            CREATE INDEX idx_tables_description_trgm ON tables USING GIN (description gin_trgm_ops);
        END IF;
    END IF;

    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'fields') THEN
        -- Create GIN indexes for full-text search on fields
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_fields_description_trgm') THEN
            CREATE INDEX idx_fields_description_trgm ON fields USING GIN (description gin_trgm_ops);
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_fields_name_trgm') THEN
            CREATE INDEX idx_fields_name_trgm ON fields USING GIN (name gin_trgm_ops);
        END IF;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Call the function to create indexes
SELECT create_search_indexes();
