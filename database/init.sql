-- BALE Database Initialization Script
-- This runs automatically when PostgreSQL container starts

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search

-- Create default admin user (for development)
-- In production, this should be done via proper user management

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE bale TO bale;

-- Set up search path
ALTER DATABASE bale SET search_path TO public;

-- Note: Actual tables are created by SQLAlchemy/Alembic
-- This file is for extensions and initial setup only
