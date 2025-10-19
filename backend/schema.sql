CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

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
                                                        ---------------- TABLES -----------------

-- Areas Table: Defines a geographic administrative region (e.g., 'Travis County').
CREATE TABLE areas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    -- The `boundary` stores the polygon shape of the administrative area.
    -- The `geography` type is optimized for calculations on a sphere (lat/lon).
    boundary GEOGRAPHY(POLYGON, 4326) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Admins Table: Stores user accounts for the admin panel.
CREATE TABLE admins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL, -- Never store plain text passwords!
    area_id UUID REFERENCES areas(id) ON DELETE RESTRICT, -- An admin must be assigned to an area.
    is_admin BOOLEAN NOT NULL DEFAULT TRUE, -- Flag to check if user is an admin
    oauth_id VARCHAR(255), -- OAuth provider's user ID
    access_token TEXT, -- OAuth access token (encrypted)
    refresh_token TEXT, -- OAuth refresh token (encrypted)
    token_expires_at TIMESTAMPTZ, -- When the access token expires
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Wells Table: The core table for every water well.
CREATE TABLE wells (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- The `location` is the exact point of the well.
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    status well_status NOT NULL DEFAULT 'draft',
    -- Capacity: How many people this well can service per day.
    capacity INTEGER NOT NULL CHECK (capacity >= 0),
    -- Current Load: How many people are currently assigned to this well.
    current_load INTEGER NOT NULL DEFAULT 0 CHECK (current_load >= 0),
    area_id UUID NOT NULL REFERENCES areas(id) ON DELETE RESTRICT,
    -- Service Area: The geographic polygon this well is responsible for.
    service_area GEOGRAPHY(POLYGON, 4326),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- WellProjects Table: For planning and cost estimation of new wells.
CREATE TABLE well_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- Links to a well that is in 'draft' status.
    well_id UUID NOT NULL UNIQUE REFERENCES wells(id) ON DELETE CASCADE,
    project_name TEXT NOT NULL,
    -- Using NUMERIC for money to avoid floating-point errors.
    estimated_build_cost NUMERIC(12, 2) NOT NULL,
    predicted_lifetime_cost NUMERIC(12, 2),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- BreakageReports Table: Stores reports submitted by users via QR code.
CREATE TABLE breakage_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    well_id UUID NOT NULL REFERENCES wells(id) ON DELETE CASCADE,
    image_url TEXT, -- URL to the photo stored in a service like S3.
    summary TEXT NOT NULL,
    status report_status NOT NULL DEFAULT 'reported',
    -- Priority is calculated by the backend algorithm based on stress.
    fix_priority INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- Step 4: Create Indexes for Performance
-- -----------------------------------------
-- Indexes are crucial for fast queries. A GIST index is specifically
-- designed for spatial data and is MANDATORY for good performance.

-- Spatial indexes
CREATE INDEX idx_areas_boundary ON areas USING GIST (boundary);
CREATE INDEX idx_wells_location ON wells USING GIST (location);
CREATE INDEX idx_wells_service_area ON wells USING GIST (service_area);

-- Standard indexes for frequently queried columns
CREATE INDEX idx_admins_area_id ON admins(area_id);
CREATE INDEX idx_wells_area_id ON wells(area_id);
CREATE INDEX idx_wells_status ON wells(status);
CREATE INDEX idx_breakage_reports_well_id ON breakage_reports(well_id);


-- Step 5: Insert Sample Data (for testing)
-- ------------------------------------------
-- This section adds some dummy data so you can start querying immediately.
-- The polygon and point data uses WKT (Well-Known Text) format with SRID 4326.

-- Insert an area for Austin, Texas
INSERT INTO areas (name, boundary) VALUES
('Travis County', ST_GeomFromText('POLYGON((-98.05 30.55, -97.45 30.55, -97.45 30.10, -98.05 30.10, -98.05 30.55))', 4326));

-- Insert a sample admin for this area
-- Note: In a real app, the password would be properly hashed by the backend.
INSERT INTO admins (email, password_hash, area_id, is_admin) VALUES
('admin@travis.gov', 'replace_with_a_real_bcrypt_hash', (SELECT id from areas WHERE name = 'Travis County'), TRUE);

-- Insert a few wells
INSERT INTO wells (location, status, capacity, current_load, area_id, service_area) VALUES
(
    ST_GeomFromText('POINT(-97.74 30.26)', 4326), -- Downtown Austin
    'completed',
    5000,
    4500,
    (SELECT id from areas WHERE name = 'Travis County'),
    ST_GeomFromText('POLYGON((-97.80 30.30, -97.70 30.30, -97.70 30.20, -97.80 30.20, -97.80 30.30))', 4326)
),
(
    ST_GeomFromText('POINT(-97.70 30.35)', 4326), -- North Austin
    'completed',
    4000,
    3200,
    (SELECT id from areas WHERE name = 'Travis County'),
    ST_GeomFromText('POLYGON((-97.75 30.40, -97.65 30.40, -97.65 30.30, -97.75 30.30, -97.75 30.40))', 4326)
),
(
    ST_GeomFromText('POINT(-97.85 30.25)', 4326), -- West Austin
    'broken',
    6000,
    5800,
    (SELECT id from areas WHERE name = 'Travis County'),
    ST_GeomFromText('POLYGON((-97.90 30.30, -97.80 30.30, -97.80 30.20, -97.90 30.20, -97.90 30.30))', 4326)
);

-- Add a breakage report for the broken well
INSERT INTO breakage_reports (well_id, summary, status, fix_priority) VALUES
(
    (SELECT id FROM wells WHERE location = ST_GeomFromText('POINT(-97.85 30.25)', 4326)),
    'User reported a cracked pump handle and no water flow.',
    'reported',
    1500 -- Example priority after an algorithm might run
);