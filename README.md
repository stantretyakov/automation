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

### Pipeline Creator

* Location: `faas/fn-pipeline-creator`
* Listens for new pipelines on the `registered-pipelines` topic,
  sends them to the LLM for conversion and creates the job via LangChain.
* Manifest: `faas/fn-pipeline-creator.yml`

## OpenFaaS Deployment

Deploy the functions using the OpenFaaS CLI. Each function has its own
deployment manifest under `faas/`:

```bash
faas-cli deploy -f faas/bridge-api.yml
faas-cli deploy -f faas/fn-core-pipeline-registrar.yml
faas-cli deploy -f faas/bridge-llm.yml
faas-cli deploy -f faas/fn-pipeline-creator.yml
```

## Configuration

Functions read their settings from environment variables. When running
locally, you can create an `env.json` file in the repository root containing
key/value pairs. Values in `env.json` are merged with `os.environ` and can be
retrieved in code via `faas.common.config.get_setting`.

Example `env.json`:

```json
{
  "KAFKA_BROKERS": "localhost:9092",
  "PIPELINE_TOPIC": "pipelines",
  "POSTGRES_DSN": "dbname=pipeline user=postgres password=postgres host=localhost"
}
```

## Database Schema

The `schema/postgres.sql` file contains a simple schema for managing
multi-tenant pipelines and their runs in PostgreSQL. It also defines
stored procedures used by the functions to persist pipeline metadata and
log requests.

## Notes

* Authentication and authorization should be integrated with Keycloak.
* Message passing between functions can be orchestrated via Kafka.
* Analytical data should be stored in a Delta Lake, while operational
  metadata can be stored in PostgreSQL.
