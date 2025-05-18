import yaml
from kafka import KafkaProducer
from faas.common import db
from faas.common.config import get_setting


def handle(event, context):
    """Entry point for bridge API.

    Expects a YAML pipeline in the request body and publishes it to Kafka
    for further processing. This function does not implement full
    orchestration; it acts as a skeleton for future logic.
    """
    pipeline_yaml = event.body.decode("utf-8")
    try:
        pipeline = yaml.safe_load(pipeline_yaml)
    except yaml.YAMLError as err:
        return f"Invalid YAML: {err}"

    tenant_id = int(get_setting("DEFAULT_TENANT_ID", "1"))
    pipeline_id = db.insert_pipeline_metadata(
        tenant_id,
        pipeline.get("name", "pipeline"),
        pipeline_yaml,
    )

    kafka_servers = get_setting("KAFKA_BROKERS", "kafka:9092").split(',')
    topic = get_setting("PIPELINE_TOPIC", "pipelines")

    producer = KafkaProducer(bootstrap_servers=kafka_servers)
    producer.send(topic, pipeline_yaml.encode("utf-8"))
    producer.flush()

    db.log_request_run(pipeline_id, "bridge-api", {"status": "accepted"})

    return {
        "status": "accepted",
        "pipeline": pipeline,
        "pipeline_id": pipeline_id,
    }
