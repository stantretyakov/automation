import psycopg2
from psycopg2 import extras
from .config import get_setting


def get_db_conn():
    dsn = get_setting(
        "POSTGRES_DSN",
        "dbname=pipeline user=postgres password=postgres host=postgres",
    )
    conn = psycopg2.connect(dsn)
    conn.autocommit = True
    return conn


def insert_pipeline_metadata(tenant_id, name, raw_yaml):
    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT insert_pipeline_metadata(%s, %s, %s)",
                (tenant_id, name, raw_yaml),
            )
            pipeline_id = cur.fetchone()[0]
    return pipeline_id


def get_pipeline_metadata(pipeline_id):
    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM get_pipeline_metadata(%s)",
                (pipeline_id,),
            )
            row = cur.fetchone()
    if row:
        return {
            "id": row[0],
            "tenant_id": row[1],
            "name": row[2],
            "raw_yaml": row[3],
            "created_at": row[4].isoformat() if row[4] else None,
        }
    return None


def log_request_run(pipeline_id, func_name, details=None):
    details_json = extras.Json(details) if details else None
    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT log_request_run(%s, %s, %s)",
                (pipeline_id, func_name, details_json),
            )

