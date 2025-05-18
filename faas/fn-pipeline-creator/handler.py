import os
import json
import yaml
import requests
from confluent_kafka import Consumer


def ask_llm(pipeline_yaml: str, external_llm: str, job_id: str, trace_id: str,
            reply_topic: str, proxy_url: str) -> None:
    payload = {
        "prompt": pipeline_yaml,
        "external_llm": external_llm,
        "reply_topic": reply_topic,
        "context": {"trace_id": trace_id},
    }
    url = f"{proxy_url}/llm/ask"
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()


def await_llm_reply(job_id: str, broker: str, reply_topic: str) -> str:
    consumer = Consumer({
        "bootstrap.servers": broker,
        "group.id": "pipeline-creator-replies",
        "auto.offset.reset": "earliest",
    })
    consumer.subscribe([reply_topic])
    try:
        while True:
            msg = consumer.poll(5.0)
            if msg is None:
                continue
            if msg.error():
                continue
            data = json.loads(msg.value().decode("utf-8"))
            if data.get("job_id") == job_id:
                consumer.commit(msg)
                return data.get("llm_response", "")
    finally:
        consumer.close()


def create_pipeline(config: str, langchain_url: str) -> dict:
    resp = requests.post(langchain_url, json={"config": config}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def handle(event, context):  # noqa: D401
    """Create pipelines based on registered specifications."""
    broker = os.getenv("KAFKA_BROKERS", "kafka:9092")
    external_llm = os.getenv("EXTERNAL_LLM", "openai")
    proxy_url = os.getenv(
        "LLM_PROXY_URL", "http://gateway:8080/function/bridge-llm-proxy"
    )
    reply_topic = os.getenv("LLM_REPLY_TOPIC", "pipeline.llm")
    langchain_url = os.getenv("LANGCHAIN_URL", "http://langchain/api/pipelines")

    consumer = Consumer({
        "bootstrap.servers": broker,
        "group.id": "fn-pipeline-creator",
        "auto.offset.reset": "earliest",
    })
    consumer.subscribe(["registered-pipelines"])

    msg = consumer.poll(1.0)
    if msg is None:
        consumer.close()
        return json.dumps({"status": "no messages"})
    if msg.error():
        consumer.close()
        return json.dumps({"status": "error", "message": str(msg.error())})

    record = json.loads(msg.value().decode("utf-8"))
    pipeline = record.get("pipeline", {})
    job_id = record.get("job_id", "")
    trace_id = record.get("trace_id", "")
    pipeline_yaml = yaml.safe_dump(pipeline)

    try:
        ask_llm(pipeline_yaml, external_llm, job_id, trace_id, reply_topic, proxy_url)
        converted = await_llm_reply(job_id, broker, reply_topic)
        result = create_pipeline(converted, langchain_url)
    except Exception as err:  # noqa: BLE001
        consumer.commit(msg)
        consumer.close()
        return json.dumps({"status": "error", "message": str(err)})

    consumer.commit(msg)
    consumer.close()
    return json.dumps({"status": "created", "job_id": job_id, "result": result})
