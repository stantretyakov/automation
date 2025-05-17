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
