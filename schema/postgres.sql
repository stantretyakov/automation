-- Schema for multi-tenant pipeline management

CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    keycloak_id UUID NOT NULL UNIQUE
);

CREATE TABLE pipelines (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    name TEXT NOT NULL,
    raw_yaml TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pipeline_runs (
    id SERIAL PRIMARY KEY,
    pipeline_id INTEGER NOT NULL REFERENCES pipelines(id),
    status TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP
);

-- Index to speed up lookups by tenant
CREATE INDEX idx_pipelines_tenant ON pipelines(tenant_id);

-- Table for storing request logs
CREATE TABLE request_logs (
    id SERIAL PRIMARY KEY,
    pipeline_id INTEGER REFERENCES pipelines(id),
    func_name TEXT NOT NULL,
    details JSONB,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stored procedure to insert pipeline metadata
CREATE OR REPLACE FUNCTION insert_pipeline_metadata(
    p_tenant_id INTEGER,
    p_name TEXT,
    p_raw_yaml TEXT
) RETURNS INTEGER AS $$
DECLARE
    new_id INTEGER;
BEGIN
    INSERT INTO pipelines(tenant_id, name, raw_yaml)
    VALUES (p_tenant_id, p_name, p_raw_yaml)
    RETURNING id INTO new_id;
    RETURN new_id;
END;
$$ LANGUAGE plpgsql;

-- Stored procedure to fetch pipeline metadata
CREATE OR REPLACE FUNCTION get_pipeline_metadata(
    p_id INTEGER
) RETURNS TABLE(
    id INTEGER,
    tenant_id INTEGER,
    name TEXT,
    raw_yaml TEXT,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY SELECT * FROM pipelines WHERE id = p_id;
END;
$$ LANGUAGE plpgsql;

-- Stored procedure to log request information
CREATE OR REPLACE FUNCTION log_request_run(
    p_pipeline_id INTEGER,
    p_func_name TEXT,
    p_details JSONB
) RETURNS VOID AS $$
BEGIN
    INSERT INTO request_logs(pipeline_id, func_name, details)
    VALUES (p_pipeline_id, p_func_name, p_details);
END;
$$ LANGUAGE plpgsql;
