import os
import json
import uuid
from datetime import datetime

import yaml
from confluent_kafka import Producer

try:
    from delta import configure_spark_with_delta_pip
    from pyspark.sql import SparkSession
except Exception:  # noqa: E722
    configure_spark_with_delta_pip = None
    SparkSession = None


def save_to_delta(pipeline_yaml: str, job_id: str, trace_id: str) -> None:
    """Append the pipeline specification to a Delta Lake table."""
    delta_path = os.getenv("DELTA_PATH", "/tmp/delta")
    workspace_id = os.getenv("WORKSPACE_ID", "default")
    target_path = os.path.join(delta_path, workspace_id)

    if SparkSession is None:
        # Delta libraries are not available; skip persistence
        return

    builder = SparkSession.builder.appName("pipeline-registrar")
    if configure_spark_with_delta_pip:
        builder = configure_spark_with_delta_pip(builder)
    spark = builder.getOrCreate()
    df = spark.createDataFrame([
        {
            "job_id": job_id,
            "trace_id": trace_id,
            "pipeline_yaml": pipeline_yaml,
            "timestamp": datetime.utcnow().isoformat(),
        }
    ])
    df.write.format("delta").mode("append").save(target_path)
    spark.stop()


def handle(event, context):  # noqa: D401
    """Register a pipeline specification."""
    body = event.body.decode("utf-8")
    try:
        pipeline = yaml.safe_load(body)
    except yaml.YAMLError as err:
        return json.dumps({"status": "error", "message": f"Invalid YAML: {err}"})

    job_id = str(uuid.uuid4())
    trace_prefix = os.getenv("TRACE_PREFIX", "trace")
    trace_id = f"{trace_prefix}-{uuid.uuid4()}"

    save_to_delta(body, job_id, trace_id)

    kafka_brokers = os.getenv("KAFKA_BROKERS", "kafka:9092")
    topic = os.getenv("PIPELINE_TOPIC", "registered-pipelines")
    producer = Producer({"bootstrap.servers": kafka_brokers})
    message = json.dumps({
        "pipeline": pipeline,
        "job_id": job_id,
        "trace_id": trace_id,
    })
    producer.produce(topic, message.encode("utf-8"))
    producer.flush()

    pipeline_id = pipeline.get("id", job_id)

    return json.dumps({
        "status": "registered",
        "trace_id": trace_id,
        "job_id": job_id,
        "pipeline_id": pipeline_id,
    })
