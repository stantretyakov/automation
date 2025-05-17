import os
import yaml
from kafka import KafkaProducer


def handle(event, context):
    """Entry point for bridge API.

    Expects a YAML pipeline in the request body and publishes it to Kafka
    for further processing. This function does not implement full
    orchestration; it acts as a skeleton for future logic.
    """
    pipeline_yaml = event.body.decode('utf-8')
    try:
        pipeline = yaml.safe_load(pipeline_yaml)
    except yaml.YAMLError as err:
        return f"Invalid YAML: {err}"

    kafka_servers = os.getenv("KAFKA_BROKERS", "kafka:9092").split(',')
    topic = os.getenv("PIPELINE_TOPIC", "pipelines")

    producer = KafkaProducer(bootstrap_servers=kafka_servers)
    producer.send(topic, pipeline_yaml.encode('utf-8'))
    producer.flush()

    return {
        "status": "accepted",
        "pipeline": pipeline,
    }
