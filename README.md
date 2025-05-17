# Data-Driven Intelligence Platform Skeleton

This repository provides a minimal skeleton for a serverless, data-driven
intelligence platform built on top of OpenFaaS. The platform accepts YAML
pipelines describing data processing steps and orchestrates them via
functions. This code is only a starting point for further development.

## Functions

### Bridge API

* Location: `faas/bridge-api`
* Accepts a YAML pipeline and publishes it to Kafka.
* Manifest: `faas/bridge-api.yml`

### Crawler

* Location: `faas/crawler`
* Placeholder implementation of a data crawler function.

## OpenFaaS Deployment

Deploy both functions using the OpenFaaS CLI:

```bash
faas-cli deploy -f faas/bridge-api.yml
```

## Database Schema

The `schema/postgres.sql` file contains a simple schema for managing
multi-tenant pipelines and their runs in PostgreSQL.

## Notes

* Authentication and authorization should be integrated with Keycloak.
* Message passing between functions can be orchestrated via Kafka.
* Analytical data should be stored in a Delta Lake, while operational
  metadata can be stored in PostgreSQL.
