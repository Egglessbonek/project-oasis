-- =============================================================================
--                  Well Management System - Database Schema (v5 - OAuth Admins)
--
-- This script integrates the new OAuth and admin fields into the 'admins' table
-- while preserving the 'weight' column in the 'wells' table and the GEOMETRY
-- data types necessary for the backend to function correctly.
--
-- =============================================================================

-- Step 0: Drop Existing Objects
DROP TABLE IF EXISTS breakage_reports CASCADE;
DROP TABLE IF EXISTS well_projects CASCADE;
DROP TABLE IF EXISTS wells CASCADE;
DROP TABLE IF EXISTS admins CASCADE;
DROP TABLE IF EXISTS areas CASCADE;

DROP TYPE IF EXISTS report_status CASCADE;
DROP TYPE IF EXISTS well_status CASCADE;


-- Step 1: Enable Necessary Extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Step 2: Create Custom Data Types
CREATE TYPE well_status AS ENUM (
    'draft',
    'building',
    'completed',
    'broken',
    'under_maintenance'
);

CREATE TYPE report_status AS ENUM (
    'reported',
    'in_progress',
    'fixed'
);

-- Step 3: Create Tables
CREATE TABLE areas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    boundary GEOMETRY(POLYGON, 4326) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- UPDATED: The new admins table with all OAuth fields
CREATE TABLE admins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    area_id UUID REFERENCES areas(id) ON DELETE RESTRICT,
    is_admin BOOLEAN NOT NULL DEFAULT TRUE,
    oauth_id VARCHAR(255),
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE wells (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location GEOMETRY(POINT, 4326) NOT NULL,
    status well_status NOT NULL DEFAULT 'draft',
    capacity INTEGER NOT NULL CHECK (capacity >= 0),
    current_load INTEGER NOT NULL DEFAULT 0 CHECK (current_load >= 0),
    weight INTEGER NOT NULL DEFAULT 0 CHECK (weight >= 0),
    area_id UUID NOT NULL REFERENCES areas(id) ON DELETE RESTRICT,
    service_area GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE well_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    well_id UUID NOT NULL UNIQUE REFERENCES wells(id) ON DELETE CASCADE,
    project_name TEXT NOT NULL,
    estimated_build_cost NUMERIC(12, 2) NOT NULL,
    predicted_lifetime_cost NUMERIC(12, 2),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE breakage_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    well_id UUID NOT NULL REFERENCES wells(id) ON DELETE CASCADE,
    image_url TEXT,
    summary TEXT NOT NULL,
    status report_status NOT NULL DEFAULT 'reported',
    fix_priority INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- Step 4: Create Indexes
CREATE INDEX idx_areas_boundary ON areas USING GIST (boundary);
CREATE INDEX idx_wells_location ON wells USING GIST (location);
CREATE INDEX idx_wells_service_area ON wells USING GIST (service_area);
CREATE INDEX idx_admins_area_id ON admins(area_id);
CREATE INDEX idx_wells_area_id ON wells(area_id);
CREATE INDEX idx_wells_status ON wells(status);
CREATE INDEX idx_breakage_reports_well_id ON breakage_reports(well_id);


-- Step 5: Insert Sample Data
INSERT INTO areas (name, boundary) VALUES
('Travis County', ST_GeomFromText('POLYGON((-98.05 30.55, -97.45 30.55, -97.45 30.10, -98.05 30.10, -98.05 30.55))', 4326));

-- UPDATED: The insert statement for the new admins table structure
INSERT INTO admins (email, password_hash, area_id, is_admin) VALUES
('admin@travis.gov', 'replace_with_a_real_bcrypt_hash', (SELECT id from areas WHERE name = 'Travis County'), TRUE);

INSERT INTO wells (location, status, capacity, weight, current_load, area_id, service_area) VALUES
(
    ST_GeomFromText('POINT(-97.74 30.26)', 4326),
    'completed',
    5000,
    5000,
    4500,
    (SELECT id from areas WHERE name = 'Travis County'),
    ST_GeomFromText('POLYGON((-97.80 30.30, -97.70 30.30, -97.70 30.20, -97.80 30.20, -97.80 30.30))', 4326)
),
(
    ST_GeomFromText('POINT(-97.70 30.35)', 4326),
    'completed',
    4000,
    4000,
    3200,
    (SELECT id from areas WHERE name = 'Travis County'),
    ST_GeomFromText('POLYGON((-97.75 30.40, -97.65 30.40, -97.65 30.30, -97.75 30.30, -97.75 30.40))', 4326)
),
(
    ST_GeomFromText('POINT(-97.85 30.25)', 4326),
    'broken',
    6000,
    0,
    5800,
    (SELECT id from areas WHERE name = 'Travis County'),
    ST_GeomFromText('POLYGON((-97.90 30.30, -97.80 30.30, -97.80 30.20, -97.90 30.20, -97.90 30.30))', 4326)
);

INSERT INTO breakage_reports (well_id, summary, status, fix_priority) VALUES
(
    (SELECT id FROM wells WHERE location = ST_GeomFromText('POINT(-97.85 30.25)', 4326)),
    'User reported a cracked pump handle and no water flow.',
    'reported',
    1500
);

