-- =====================================================================
-- Alpha Terra Real Estate Intelligence Engine: Canonical Data Model
-- Target Dialect: PostgreSQL 15+ with PostGIS Extension
-- =====================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis;

-- 1. LOCALITIES
CREATE TABLE localities (
    locality_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    locality_name VARCHAR(100) NOT NULL UNIQUE,
    micro_market VARCHAR(100) NOT NULL,
    pincode VARCHAR(10),
    boundary GEOMETRY(Polygon, 4326),
    centroid GEOMETRY(Point, 4326) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. DEVELOPERS
CREATE TABLE developers (
    developer_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    canonical_name VARCHAR(255) NOT NULL,
    cin_number VARCHAR(21) UNIQUE,
    track_record_score NUMERIC(3, 2) DEFAULT 3.00,
    active_projects_count INT DEFAULT 0,
    completed_projects_count INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. PROJECTS
CREATE TABLE projects (
    project_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    developer_id UUID REFERENCES developers(developer_id) ON DELETE SET NULL,
    locality_id UUID REFERENCES localities(locality_id) ON DELETE RESTRICT,
    canonical_project_name VARCHAR(255) NOT NULL,
    rera_registration_number VARCHAR(100) UNIQUE,
    total_towers INT,
    total_sanctioned_units INT,
    launch_date DATE,
    sanctioned_completion_date DATE,
    revised_completion_date DATE,
    coordinates GEOMETRY(Point, 4326) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. CANONICAL PROPERTIES (Physical Units)
CREATE TABLE canonical_properties (
    property_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(project_id) ON DELETE SET NULL,
    locality_id UUID REFERENCES localities(locality_id) ON DELETE RESTRICT,
    unit_number VARCHAR(50),
    tower_block VARCHAR(50),
    bhk_type VARCHAR(20) NOT NULL,
    carpet_area_sqft NUMERIC(10, 2) NOT NULL,
    super_built_up_sqft NUMERIC(10, 2),
    floor_number INT,
    total_floors INT,
    facing_direction VARCHAR(20),
    coordinates GEOMETRY(Point, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_physical_unit UNIQUE (project_id, tower_block, unit_number)
);

-- 5. LISTINGS (Marketplace Representations)
CREATE TABLE listings (
    listing_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID REFERENCES canonical_properties(property_id) ON DELETE CASCADE,
    source_platform VARCHAR(50) NOT NULL,
    source_listing_id VARCHAR(100) NOT NULL,
    listing_url TEXT,
    listing_status VARCHAR(30) DEFAULT 'ACTIVE',
    current_asking_price NUMERIC(15, 2) NOT NULL,
    carpet_area_sqft NUMERIC(10, 2) NOT NULL,
    current_psf_price NUMERIC(10, 2) GENERATED ALWAYS AS (current_asking_price / NULLIF(carpet_area_sqft, 0)) STORED,
    furnishing_status VARCHAR(50),
    first_listed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_verified_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT uq_source_listing UNIQUE (source_platform, source_listing_id)
);

-- 6. PRICE OBSERVATIONS (Append-Only Historical Log)
CREATE TABLE price_observations (
    observation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    listing_id UUID REFERENCES listings(listing_id) ON DELETE CASCADE,
    observed_price NUMERIC(15, 2) NOT NULL,
    observed_psf NUMERIC(10, 2) NOT NULL,
    is_price_drop BOOLEAN DEFAULT FALSE,
    observation_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. MARKET TRANSACTION RECORDS (SRO / Deed Registry Data)
CREATE TABLE transaction_records (
    transaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(project_id) ON DELETE SET NULL,
    locality_id UUID REFERENCES localities(locality_id) ON DELETE RESTRICT,
    deed_registration_number VARCHAR(100) UNIQUE,
    registration_date DATE NOT NULL,
    sale_consideration_price NUMERIC(15, 2) NOT NULL,
    guidance_market_value NUMERIC(15, 2),
    registered_carpet_area_sqft NUMERIC(10, 2),
    transaction_psf NUMERIC(10, 2) GENERATED ALWAYS AS (sale_consideration_price / NULLIF(registered_carpet_area_sqft, 0)) STORED,
    stamp_duty_paid NUMERIC(12, 2),
    registration_fee_paid NUMERIC(12, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. INDEXES
CREATE INDEX idx_projects_geom ON projects USING GIST (coordinates);
CREATE INDEX idx_properties_geom ON canonical_properties USING GIST (coordinates);
CREATE INDEX idx_listings_property_id ON listings(property_id);
CREATE INDEX idx_price_observations_listing_id ON price_observations(listing_id, observation_timestamp);
CREATE INDEX idx_transactions_registration_date ON transaction_records(locality_id, registration_date);